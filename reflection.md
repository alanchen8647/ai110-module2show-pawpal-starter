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

* I made change on the design mainly on the formating of the attribute, my Ai assistant told me that I need to pay extra attention on how I set up the time for each of the tasks, simply one attribute for startTime/endTime is not enoguh I need also to take account on the minutes, and actual duration to be able to detect conflict when putting them in a plan. It also pointed out removing unnecessary attributes when it's within reach to trace, such as removing owner_id in tasks since it's traceable in pet's attribute. I also added a list of pets to the PetOwner class to create a two-way link, making it easier to trace pets under a single owner. 

* for other small issue, I renamed a few method that shares similar name.

**Sample Output**
```
Today's Schedule (2026-10-18) for Alex
------------------------------------------------------------
07:30-08:00  Rex      walk       priority 5
                   note: Use the red leash
08:00-08:15  Rex      feeding    priority 5
                   note: Half cup of kibble
12:00-12:05  Miso     medication priority 5
                   note: Give with a treat
18:00-18:20  Miso     grooming   priority 2
------------------------------------------------------------
```
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- The Plan Schedule picks its tasks using the classic greedy algorithm; that algorithm is fast and simple but doesn't guarantee the most greedy result. For example, sometimes it would choose the tasks with priority 5 when it could have chosen the other 2 tasks with priority 4 in the same slot. But I still decided to keep this procedure because it follows the real-life business operation, which when a tasks has higher priority it should be execute a head of all other tasks. 

---

## 3. AI Collaboration

**a. How you used AI**

- I used Claude Code for debugging and refactoring the current existing structure that I first came up, the most common and important usage is asking Claude to identify missinng relationship and logic bottlenect that might leads to complicated issue when implementation. 
- I basically asked Claude Code to play the role as my developer buddy, discuss with me on what part of the code in your aspect are unclear or can be improved. I will read through its suggestions and give it my opinion on why I set it up that way. On important issue that it did point out, I discussed on it how I want it to fix the problem, and asked it to double-check the achievability of the solution. On the area that I wasn’t clear on, I asked it to come up with how it would fix the problem. 

**b. Judgment and verification**

- Claude did point out some severe issues that I didn’t consider in the initial design, such as the missing precision in time measurement (hour instead of hour+minutes) that might lead to difficulty when ordering tasks for a daily plan. But then there are also areas in which AI points out a complicating issue, such as adding an extra layer of class called Store and move factory method into that new class. That would increase the complexity of the project setup from 4 classes to 5 classes, and it involves an area beyond my knowledge. I asked AI if this is a critical issue to determine the importance of this improvement, and decided to skip it after it replied that this is a readability issue.

---

## 4. Testing and Verification

**a. What you tested**

This runs tests on:
* Sorting in chronological order
* Sorting keeps the original order with same start time
* Sorting in time order
* Recurrence set up for completing daily task
* Recurrence set up for completing weekly task
* handling leap day 
* one time task does not create next courrance
* Completing a recurring task twice creates only one next occurrence
* Reopening and re-completing doesn't duplicate
* recurring task with no due date, counts the day it wasa completed
* invalid recurrence values will be rejected
* Completing plan returns next occurrences for recurring tasks only
* adding a task with same pet, type, and start time raises an error
* Two pets with same start time falg as conflict
* Back-to-Back tasks don't conflict
* Higher priority task bumps an overlapping lower-priority one
* lower prioirty task that overlaps a higher one is rejected
* bumping works as a chain, and the greedy rebuild keeps the higher priority tasks.
* untimed task will be rejected
* Finding a free time gap returns the earliest fit
* Filtering by status or pet name works, and invalid status will be reject.

**b. Confidence**

Conflident: 4/5 stars


---

## 5. Reflection

**a. What went well**

- Setting up the greedy algorithm is the part that I spent the most time on, deciding what approach the algorithm can take to achieve a better schedule following real-life operational logic. I also have a deep conversation with AI about areas for improvement, solution achivability, and if it's necessary to solve a complicated problem or leave it for the future.

**b. What you would improve**

- I checked the UI and the actual program use case at the last step; that's where I find out that I missed out an important part of the project: that it remembers the tasks for unselected. As for now if user trying to add a task that doesn't fit in to current schedule, the program will completely reject this tasks as it has conflict with current schedule. But in real-life operaiton, it should of keep that tasks on schedule, and wait for an chance to fit that tasks in future schedule. If I have a chance in the future, I will first check the UI and consider the user interaction while brainstorming the structure.

**c. Key takeaway**
- It's really important to make a precise plan at the beginning. It will make everything complicated if a potential bug or logic bottleneck is found out at the last moment of the project, which it might require a rework that will trace down to the original UML design of the project. 