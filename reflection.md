# PawPal+ Project Reflection

## 1. System Design

Three core actions:
1. They should be able to add a pet with a name, breed, and other attributes
2. They should be able to schedule things to do for them like feed them and take them on a walk
3. They should be able to see their task they need to take care of them for today so they don't forget

Brainstorm: 
Tasks class: 
    Lets us schedule tasks for the pet and update any information we need

Pet class: 
    Holds name, breed, weight, etc information to update later
    Inherits tasks

**a. Initial design**

- Briefly describe your initial UML design.
Owner class that takes care of everything, and then other classes that handle information like scheduling tasks, and pet information.
- What classes did you include, and what responsibilities did you assign to each?
Owner class: The class that takes all the information from other classes
Pet class: Stores information about the pet
Task class: Stores information about the tasks
Other classes to handle daily schedules and schedule items

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
Yes. I added a `due_date` to Task so daily and weekly tasks could repeat, and a `warnings` list on DailyPlan so conflicts show up with the plan. I also added a few Scheduler methods (sorting by time, filtering, and conflict checks) that weren't in my first UML.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?
The scheduler looks at the time the owner has available, task priority, preferred times, and each task's due date. Time available matters most because it can't be bent, then priority so the important stuff like medication always makes the cut, then preferred times since those are only nice to have.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
The scheduler only warns about conflicts instead of resolving them, and it only checks tasks that have a preferred time. When two timed tasks overlap, the plan quietly pushes the later one back (for example a 8:15 vet call starts at 8:30 after the 8:00 walk) and `find_time_conflicts()` reports the overlap as a warning. Tasks without a preferred time are never flagged because the scheduler places them itself.
- Why is that tradeoff reasonable for this scenario?
A pet owner knows things the scheduler doesn't (the vet call can't actually move, the walk can). Auto-rearranging could silently break a real appointment, while a clear warning lets the owner decide. Pairwise checking is also simple and fast enough for the handful of tasks one household has in a day.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?
I used AI to brainstorm the classes, turn my UML into code, and write tests. The most helpful prompts were specific ones, like "what edge cases should I test for this method?" instead of "make it better."

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
The AI suggested having the scheduler automatically move conflicting tasks to a new time. I changed it to just warn the owner, since the owner knows which task can actually move. I checked suggestions by running main.py and the tests instead of trusting that the code looked right.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?
I tested sorting, recurring tasks, conflict detection, the time budget, and edge cases like empty pets, tasks running past midnight, and invalid updates. These matter because the whole app depends on the schedule being right, and a wrong schedule means a missed feeding or medication.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?
Pretty confident, 5/5 for what I tested since all 38 tests pass. Next I'd test the Streamlit app itself and what happens when a recurring task is completed late.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
The Scheduler. It's easy to read, each method does one thing, and the UI just calls it.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I'd let the scheduler suggest a new time for a conflicting task, and let owners edit or delete tasks in the app. I'd also make recurring tasks count from their original due date.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
AI is fast, but I still have to be the lead architect and make the design calls. What worked best was keeping separate chat sessions for each phase (design, building, testing, polish) so each one stayed focused. The AI features that helped most were generating code from my UML, writing tests, and catching edge cases I missed. I learned to treat its suggestions as drafts, check them against my design, and say no when they make things more complicated.
