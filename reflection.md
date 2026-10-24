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

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
