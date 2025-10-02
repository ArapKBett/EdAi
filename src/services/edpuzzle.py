from src.services.clever import CleverService
import asyncio
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class EdpuzzleService(CleverService):
    def __init__(self):
        super().__init__()
        self.edpuzzle_loaded = False
    
    async def navigate_to_edpuzzle(self) -> bool:
        """Navigate to Edpuzzle through Clever"""
        try:
            success = await self.launch_application('edpuzzle')
            if success:
                # Wait for Edpuzzle to load completely
                await self.page.wait_for_timeout(10000)
                
                # Check if we're on an Edpuzzle page
                current_url = self.page.url
                if 'edpuzzle.com' in current_url:
                    self.edpuzzle_loaded = True
                    logger.info("Successfully navigated to Edpuzzle")
                    return True
                else:
                    # Try to detect Edpuzzle by page content
                    page_content = await self.page.content()
                    if 'edpuzzle' in page_content.lower():
                        self.edpuzzle_loaded = True
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error navigating to Edpuzzle: {e}")
            return False
    
    async def get_video_assignments(self) -> List[Dict]:
        """Get video assignments from Edpuzzle"""
        try:
            if not self.edpuzzle_loaded and not await self.navigate_to_edpuzzle():
                return []
            
            # Wait for assignments to load
            await self.page.wait_for_timeout(5000)
            
            # Try multiple strategies to find video assignments
            assignments = await self.page.evaluate('''() => {
                const assignments = [];
                
                // Strategy 1: Look for assignment cards
                const assignmentSelectors = [
                    '.assignment-item',
                    '.video-assignment',
                    '[class*="assignment"]',
                    '.media-assignment',
                    '.task-item'
                ];
                
                for (const selector of assignmentSelectors) {
                    const elements = document.querySelectorAll(selector);
                    for (const element of elements) {
                        const titleElement = element.querySelector('.video-title, .title, h3, h4, [class*="title"]');
                        const teacherElement = element.querySelector('.teacher-name, .instructor, [class*="teacher"]');
                        const dueDateElement = element.querySelector('.due-date, .date, [class*="due"]');
                        const questionsElement = element.querySelector('.questions, .questions-count, [class*="question"]');
                        const progressElement = element.querySelector('.progress, .completion, [class*="progress"]');
                        const linkElement = element.querySelector('a');
                        
                        if (titleElement) {
                            assignments.push({
                                title: titleElement.innerText?.trim() || '',
                                teacher: teacherElement?.innerText?.trim() || '',
                                due_date: dueDateElement?.innerText?.trim() || '',
                                questions_count: questionsElement?.innerText?.trim() || '',
                                progress: progressElement?.innerText?.trim() || 'Not Started',
                                link: linkElement?.href || '',
                                platform: 'Edpuzzle'
                            });
                        }
                    }
                    
                    if (assignments.length > 0) break;
                }
                
                // Strategy 2: Look for video thumbnails
                if (assignments.length === 0) {
                    const videoElements = document.querySelectorAll('.video-thumbnail, [class*="video"], .media-item');
                    for (const element of videoElements) {
                        const titleElement = element.querySelector('.title, h3, h4, [class*="title"]');
                        const contextElement = element.closest('.assignment, .task') || element.parentElement;
                        
                        if (titleElement) {
                            assignments.push({
                                title: titleElement.innerText?.trim() || '',
                                teacher: '',
                                due_date: '',
                                questions_count: '',
                                progress: 'Unknown',
                                link: element.querySelector('a')?.href || '',
                                platform: 'Edpuzzle'
                            });
                        }
                    }
                }
                
                return assignments;
            }''')
            
            # Filter out empty titles
            assignments = [assignment for assignment in assignments if assignment.get('title')]
            
            logger.info(f"Found {len(assignments)} Edpuzzle assignments")
            return assignments
            
        except Exception as e:
            logger.error(f"Error getting Edpuzzle assignments: {e}")
            return []
    
    async def watch_video_assignment(self, assignment_title: str) -> bool:
        """Start watching a video assignment"""
        try:
            if not self.edpuzzle_loaded and not await self.navigate_to_edpuzzle():
                return False
            
            assignments = await self.get_video_assignments()
            target_assignment = next(
                (assignment for assignment in assignments if assignment_title.lower() in assignment['title'].lower()),
                None
            )
            
            if target_assignment and target_assignment.get('link'):
                await self.page.goto(target_assignment['link'])
                await self.page.wait_for_timeout(5000)
                logger.info(f"Started video assignment: {assignment_title}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error starting video assignment: {e}")
            return False
    
    async def answer_video_questions(self, assignment_title: str, answers: Dict) -> bool:
        """Answer questions in a video assignment (placeholder implementation)"""
        try:
            if not await self.watch_video_assignment(assignment_title):
                return False
            
            logger.info(f"Attempting to answer questions for: {assignment_title}")
            # Note: Actual implementation would require specific interaction
            # with Edpuzzle's question interface
            
            # This is a placeholder - in practice, you'd need to:
            # 1. Detect when questions appear
            # 2. Match questions with provided answers
            # 3. Submit answers appropriately
            
            return True
            
        except Exception as e:
            logger.error(f"Error answering video questions: {e}")
            return False
    
    async def get_video_progress(self) -> List[Dict]:
        """Get progress on video assignments"""
        try:
            if not self.edpuzzle_loaded and not await self.navigate_to_edpuzzle():
                return []
            
            progress_data = await self.page.evaluate('''() => {
                const progress = [];
                const progressSelectors = [
                    '.progress-bar',
                    '.completion-status',
                    '[class*="progress"]',
                    '[class*="completion"]'
                ];
                
                for (const selector of progressSelectors) {
                    const elements = document.querySelectorAll(selector);
                    for (const element of elements) {
                        const context = element.closest('.assignment, .video-item') || element.parentElement;
                        const titleElement = context?.querySelector('.title, h3, h4');
                        
                        if (titleElement) {
                            progress.push({
                                title: titleElement.innerText?.trim() || '',
                                progress: element.innerText?.trim() || element.getAttribute('aria-valuenow') || '0',
                                element: selector
                            });
                        }
                    }
                }
                
                return progress;
            }''')
            
            return progress_data
            
        except Exception as e:
            logger.error(f"Error getting video progress: {e}")
            return []
