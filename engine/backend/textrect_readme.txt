Title: Module for rendering wordwrapped text
Author: David Clark (silenus@telus.net)
Submission date: May 23, 2001

Description: Tries to render the supplied text string in the passed rect, by word-wrapping where possible.  Interprets an embedded \n as a linefeed.  Displays the final text left or right justified, or centered.

pygame version required: Any, with pygame.font
SDL version required: Any
Python version required: Any

**********************************************************
Proyect Mano-Gift modifications
In order to make use of this module, we had to make the following changes:

- line3: added BaseException as inheritance for TextRectException. (syntax error)
- line47: replaced , with ( and added a ) at the end of line. (syntax error)
- line70: replaced , with ( and added a ) at the end of line. (syntax error)
- line80: replaced , with ( and added a ) at the end of line. (syntax error)
- line87: added import sys
- line110-111: added pygame.quit() and sys.exit()