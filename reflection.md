# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

* The system will have multiple classes including, pet, pet tasks, pet owner, plan schedule. 

* Pet class will contain information of a individual pet, inclduing their pet id, name, breed, age, and client id of the pet owner that owns this pet.

* Pet-Owner class will contain informaiton of a invidual pet-owner/client, information include name, gender, client id. 

* Pet tasks class will contain information of a single pet care tasks, it would contain the information of it's own task id, the pet & owner id of the task owner pet, status of the complation of this task, task type (etc: walks), area this task will be performed, estimated time duration of this task will take, priority of the tasks, and any owner preferences for this given tasks. 

* Plan schedule tasks will contain information of a built plan for a day, each item in this class is a full day schedule of pet care tasks. This class will include a schedule ID, date, schedule status, and a set of tasks in order of priority and time range. 

* The 3 main core actions will be add pet, add pet tasks, and create plan with tasks.


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
