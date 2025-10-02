from src.services.clever import CleverService
import asyncio
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class McGrawHillService(CleverService):
    def __init__(self):
        super().__init__()
        self.mcgraw_hill_loaded = False
    
    async def navigate_to_mcgraw_hill(self) -> bool:
        """Navigate to McGraw Hill through Clever"""
        try:
            success = await self.launch_application('mcgraw hill')
            if success:
                # Wait for McGraw Hill to load completely
                await self.page.wait_for_timeout(10000)
                
                # Check if we're on a McGraw Hill page
                current_url = self.page.url
                if 'mheducation.com' in current_url or 'connected.mcgraw-hill.com' in current_url:
                    self.mcgraw_hill_loaded = True
                    logger.info("Successfully navigated to McGraw Hill")
                    return True
                else:
                    # Try to detect McGraw Hill by page content
                    page_content = await self.page.content()
                    if any(keyword in page_content.lower() for keyword in ['mcgraw', 'mheducation', 'connected']):
                        self.mcgraw_hill_loaded = True
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error navigating to McGraw Hill: {e}")
            return False
    
    async def get_assignments(self) -> List[Dict]:
        """Get assignments from McGraw Hill"""
        try:
            if not self.mcgraw_hill_loaded and not await self.navigate_to_mcgraw_hill():
                return []
            
            # Wait for assignments to load
            await self.page.wait_for_timeout(5000)
            
            # Try multiple strategies to find assignments
            assignments = await self.page.evaluate('''() => {
                const assignments = [];
                
                // Strategy 1: Look for assignment cards or list items
                const assignmentSelectors = [
                    '.assignment',
                    '.task',
                    '.homework',
                    '[class*="assignment"]',
                    '[class*="task"]',
                    '[class*="homework"]',
                    '.activity-item',
                    '.work-item'
                ];
                
                for (const selector of assignmentSelectors) {
                    const elements = document.querySelectorAll(selector);
                    for (const element of elements) {
                        const titleElement = element.querySelector('.title, h3, h4, [class*="title"], [class*="name"]');
                        const dueDateElement = element.querySelector('.due-date, .date, [class*="due"], [class*="date"]');
                        const statusElement = element.querySelector('.status, .state, [class*="status"]');
                        const linkElement = element.querySelector('a');
                        
                        if (titleElement) {
                            assignments.push({
                                title: titleElement.innerText?.trim() || '',
                                due_date: dueDateElement?.innerText?.trim() || '',
                                status: statusElement?.innerText?.trim() || 'Assigned',
                                link: linkElement?.href || '',
                                platform: 'McGraw Hill'
                            });
                        }
                    }
                    
                    if (assignments.length > 0) break;
                }
                
                // Strategy 2: Look for table rows
                if (assignments.length === 0) {
                    const rows = document.querySelectorAll('tr');
                    for (const row of rows) {
                        const cells = row.querySelectorAll('td');
                        if (cells.length >= 2) {
                            const titleCell = cells[0];
                            const dateCell = cells[1];
                            const link = titleCell.querySelector('a');
                            
                            if (titleCell.innerText?.trim() && !titleCell.innerText.trim().match(/^(title|name|assignment)$/i)) {
                                assignments.push({
                                    title: titleCell.innerText.trim(),
                                    due_date: dateCell.innerText?.trim() || '',
                                    status: 'Assigned',
                                    link: link?.href || '',
                                    platform: 'McGraw Hill'
                                });
                            }
                        }
                    }
                }
                
                return assignments;
            }''')
            
            # Filter out empty titles and duplicates
            seen_titles = set()
            unique_assignments = []
            
            for assignment in assignments:
                if assignment.get('title') and assignment['title'] not in seen_titles:
                    seen_titles.add(assignment['title'])
                    unique_assignments.append(assignment)
            
            logger.info(f"Found {len(unique_assignments)} McGraw Hill assignments")
            return unique_assignments
            
        except Exception as e:
            logger.error(f"Error getting McGraw Hill assignments: {e}")
            return []
    
    async def complete_assignment(self, assignment_title: str, answers: Dict) -> bool:
        """Complete a McGraw Hill assignment (placeholder implementation)"""
        try:
            if not self.mcgraw_hill_loaded and not await self.navigate_to_mcgraw_hill():
                return False
            
            logger.info(f"Attempting to complete McGraw Hill assignment: {assignment_title}")
            # Note: Actual implementation would require specific knowledge of
            # McGraw Hill's interface and should be used responsibly
            
            return True
            
        except Exception as e:
            logger.error(f"Error completing McGraw Hill assignment: {e}")
            return False
    
    async def get_course_materials(self) -> List[Dict]:
        """Get available course materials from McGraw Hill"""
        try:
            if not self.mcgraw_hill_loaded and not await self.navigate_to_mcgraw_hill():
                return []
            
            materials = await self.page.evaluate('''() => {
                const materials = [];
                const materialSelectors = [
                    '.chapter',
                    '.lesson',
                    '.material',
                    '.resource',
                    '[class*="chapter"]',
                    '[class*="lesson"]'
                ];
                
                for (const selector of materialSelectors) {
                    const elements = document.querySelectorAll(selector);
                    for (const element of elements) {
                        const titleElement = element.querySelector('.title, h3, h4, [class*="title"]');
                        const descriptionElement = element.querySelector('.description, [class*="description"]');
                        const linkElement = element.querySelector('a');
                        
                        if (titleElement) {
                            materials.push({
                                title: titleElement.innerText?.trim() || '',
                                description: descriptionElement?.innerText?.trim() || '',
                                link: linkElement?.href || '',
                                type: 'material'
                            });
                        }
                    }
                }
                
                return materials;
            }''')
            
            return materials
            
        except Exception as e:
            logger.error(f"Error getting course materials: {e}")
            return []
