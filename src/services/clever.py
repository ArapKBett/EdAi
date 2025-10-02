from playwright.async_api import async_playwright
import asyncio
from src.config.settings import settings
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class CleverService:
    def __init__(self):
        self.username = settings.CLEVER_USERNAME
        self.password = settings.CLEVER_PASSWORD
        self.browser = None
        self.page = None
        self.is_logged_in = False
    
    async def login(self) -> bool:
        """Login to Clever portal"""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            self.page = await self.browser.new_page()
            
            # Set longer timeout for educational sites
            self.page.set_default_timeout(60000)
            
            # Navigate to Clever login
            await self.page.goto('https://clever.com/in/edu-login')
            await self.page.wait_for_timeout(3000)
            
            # Look for login form elements
            username_selectors = [
                'input[name="username"]',
                'input[type="text"]',
                'input[placeholder*="username" i]',
                'input[placeholder*="email" i]',
                '#username',
                '.username-input'
            ]
            
            password_selectors = [
                'input[name="password"]',
                'input[type="password"]',
                'input[placeholder*="password" i]',
                '#password',
                '.password-input'
            ]
            
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Log In")',
                'button:has-text("Sign In")',
                '.login-button'
            ]
            
            # Try to find and fill login form
            username_filled = False
            password_filled = False
            
            for selector in username_selectors:
                if await self.page.query_selector(selector):
                    await self.page.fill(selector, self.username)
                    username_filled = True
                    break
            
            for selector in password_selectors:
                if await self.page.query_selector(selector):
                    await self.page.fill(selector, self.password)
                    password_filled = True
                    break
            
            if not username_filled or not password_filled:
                logger.error("Could not find login form elements")
                return False
            
            # Submit login form
            for selector in submit_selectors:
                if await self.page.query_selector(selector):
                    await self.page.click(selector)
                    break
            
            # Wait for login to complete
            await self.page.wait_for_timeout(8000)
            
            # Check if login was successful
            current_url = self.page.url
            if 'portal' in current_url or 'dashboard' in current_url or 'clever.com' in current_url:
                self.is_logged_in = True
                logger.info("Successfully logged into Clever")
                return True
            else:
                # Check for error messages
                error_selectors = [
                    '.error',
                    '.alert-error',
                    '[class*="error"]',
                    'text=*error*i',
                    'text=*invalid*i',
                    'text=*incorrect*i'
                ]
                
                for selector in error_selectors:
                    error_element = await self.page.query_selector(selector)
                    if error_element:
                        error_text = await error_element.text_content()
                        logger.error(f"Login error: {error_text}")
                        return False
                
                logger.warning("Login status uncertain, continuing anyway")
                self.is_logged_in = True
                return True
                
        except Exception as e:
            logger.error(f"Clever login failed: {e}")
            return False
    
    async def get_applications(self) -> List[Dict]:
        """Get list of available applications in Clever portal"""
        try:
            if not self.is_logged_in and not await self.login():
                return []
            
            # Navigate to applications page
            await self.page.goto('https://clever.com/applications')
            await self.page.wait_for_timeout(5000)
            
            # Extract application information using multiple selector strategies
            apps = await self.page.evaluate('''() => {
                const apps = [];
                
                // Strategy 1: Look for app cards
                const appCards = document.querySelectorAll('[data-testid="app-card"], .app-card, [class*="app"], .application');
                
                for (const card of appCards) {
                    const nameElement = card.querySelector('h3, h4, .app-name, [class*="name"], .title');
                    const descriptionElement = card.querySelector('p, .app-description, [class*="description"]');
                    const linkElement = card.querySelector('a');
                    
                    if (nameElement) {
                        apps.push({
                            name: nameElement.innerText?.trim() || '',
                            description: descriptionElement?.innerText?.trim() || '',
                            link: linkElement?.href || '',
                            icon: linkElement?.querySelector('img')?.src || ''
                        });
                    }
                }
                
                // Strategy 2: Look for grid items
                if (apps.length === 0) {
                    const gridItems = document.querySelectorAll('.grid-item, .tile, .app-tile');
                    for (const item of gridItems) {
                        const link = item.querySelector('a');
                        if (link) {
                            const name = link.innerText?.trim() || link.getAttribute('title') || '';
                            if (name) {
                                apps.push({
                                    name: name,
                                    description: '',
                                    link: link.href,
                                    icon: link.querySelector('img')?.src || ''
                                });
                            }
                        }
                    }
                }
                
                return apps;
            }''')
            
            # Filter out empty results
            apps = [app for app in apps if app.get('name')]
            
            logger.info(f"Found {len(apps)} applications in Clever portal")
            return apps
            
        except Exception as e:
            logger.error(f"Error getting Clever applications: {e}")
            return []
    
    async def launch_application(self, app_name: str) -> bool:
        """Launch a specific application by name"""
        try:
            if not self.is_logged_in and not await self.login():
                return False
            
            apps = await self.get_applications()
            target_app = next(
                (app for app in apps if app_name.lower() in app['name'].lower()),
                None
            )
            
            if target_app and target_app.get('link'):
                await self.page.goto(target_app['link'])
                await self.page.wait_for_timeout(8000)
                logger.info(f"Launched application: {app_name}")
                return True
            
            logger.warning(f"Application not found: {app_name}")
            return False
            
        except Exception as e:
            logger.error(f"Error launching application {app_name}: {e}")
            return False
    
    async def get_current_page_content(self) -> Optional[str]:
        """Get the current page content for debugging"""
        try:
            if self.page:
                return await self.page.content()
            return None
        except Exception as e:
            logger.error(f"Error getting page content: {e}")
            return None
    
    async def close(self):
        """Close the browser"""
        try:
            if self.browser:
                await self.browser.close()
                self.is_logged_in = False
                logger.info("Clever browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
