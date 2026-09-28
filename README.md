# FYE 100 Pathfinder Guidebook

> Students see **Modules** (matching Blackboard). The folders are still named `chapters/ch01` and so on, so published links keep working.

The digital textbook for **FYE 100: Strategies for College Success** at Owensboro Community & Technical College.

**Live site:** https://octc-id.github.io/FYE100-pathfinder-guidebook/

Blackboard holds the assignments, due dates, and grades. This guidebook holds the reading. Each Blackboard module links to its chapter opener, for example:

```
https://octc-id.github.io/FYE100-pathfinder-guidebook/chapters/ch04/
```

> The repository name in the link is **case-sensitive**. `FYE100-pathfinder-guidebook` works; `fye100-pathfinder-guidebook` does not.

## Structure

```
index.html              Book home: cover and full table of contents
css/styles.css          One stylesheet for every page
js/book.js              Sidebar behavior and section highlighting
images/shared/          Logos and images used across the book
images/shared/10es/     10 Essential Skills coin icons, 10es-01.png to 10es-10.png
images/chNN/            Images for one chapter
chapters/chNN/
  index.html            Chapter opener (why it matters, objectives, skills, lessons)
  N-1.html, N-2.html    Lessons
  trail-tip.html        Trail Tip (when a chapter has one)
faculty/alignment.html  Objective → lesson → 10ES → BE map (planned)
```

## Rules

1. **Never rename or move a published file or folder.** Blackboard links point to these exact paths in every course shell.
2. **Lowercase, with hyphens instead of spaces**, for every new file and folder. Chapter folders use two digits: `ch01` through `ch12`.
3. **No dates, deadlines, or point values in the book.** Those live in Blackboard, so the book works every term without edits. Mile Marker pages may name the assignment and describe it, but always send students to Blackboard for the due date.
4. **Learning objectives come from the FYE 100 Competency Framework, word for word.**
5. **Every link that leaves the book opens in a new tab.** Use `target="_blank" rel="noopener"` plus `<span class="sr-only"> (opens in a new tab)</span>` inside the link. Links between pages of the book stay in the same tab. (`js/book.js` also enforces this as a backup.)
6. **After any change to `css/styles.css` or `js/book.js`**, raise the `?v=` number on every page (for example, `styles.css?v=1` to `styles.css?v=2`) so browsers load the new version.

## Updating the site

1. Edit and preview the files locally in a browser.
2. Upload them in GitHub: open the matching folder, choose **Add file → Upload files**, and drag them in. To add a new folder, drag the folder itself.
3. Check the **Actions** tab for a green check (about 1–2 minutes).
4. Hard-refresh the live page (Ctrl+Shift+R, or Cmd+Shift+R on a Mac).

## Page anatomy

- **Chapter sidebar** on the left: the chapter's lessons, plus the current lesson's sections. It becomes a "Lessons" button on phones.
- **Margin notes** on the right (`.note-term`, `.note-tip`, `.note-see`) for Key Terms, Pathfinder Tips, and See Also links. They move into the text on smaller screens.
- **Rest-stop dividers** (`<span class="rest">`) between major sections, for breathing room.
- **Sticky-note blocks** (`.sticky`) for "Why this matters" and for stops in the reading such as Reflect.
- **10 Essential Skills** always appear with their coin icon and number (`.coin`, `.coin-sm`), and use the official CPE names word for word.
- **Mile Marker pages** (`mile-marker.html`) present the assignment with support, then a fill-in form. `js/book.js` saves typing in the student's browser, requires a name, and saves the PDF with the title "Mile Marker #N - Name".
- The **last page of each module** ends the reading path with a link back to the book contents.
