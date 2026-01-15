# Example Quiz Output

This shows what quiz generation produces for a single chapter.

## Example: Chapter 3 - ROS 2 Topics Quiz

### Quiz Metadata
- **Chapter ID:** `chapter-03-ros2-topics`
- **Title:** ROS 2 Topics Quiz
- **Instructions:** Test your understanding of the chapter concepts. Good luck!
- **Passing Score:** 70%
- **Total Questions:** 8
- **Total Points:** 8

---

### Question 1 (Multiple Choice - Intermediate)

**Question:** What is the primary purpose of ROS 2 topics?

**Options:**
A. To enable synchronous request-response communication between nodes
B. To enable asynchronous publish-subscribe communication between nodes
C. To store persistent data in the ROS 2 system
D. To manage node lifecycle and execution

**Correct Answer:** B

**Explanation:**
ROS 2 topics implement the publish-subscribe pattern, enabling asynchronous, many-to-many communication between nodes. Publishers send messages to topics without knowing who will receive them, and subscribers receive messages from topics they're interested in. This is fundamentally different from services (request-response) and differs from data storage or lifecycle management.

**Points:** 1

---

### Question 2 (True/False - Beginner)

**Question:** True or False: In ROS 2, a topic can have multiple publishers but only one subscriber.

**Options:**
A. True
B. False

**Correct Answer:** B (False)

**Explanation:**
This statement is false. ROS 2 topics support many-to-many communication, meaning a topic can have:
- Multiple publishers sending messages to the same topic
- Multiple subscribers receiving messages from the same topic
- Or any combination (1-to-many, many-to-1, many-to-many)

This flexibility is one of the key advantages of the publish-subscribe pattern.

**Points:** 1

---

### Question 3 (Code Completion - Intermediate)

**Question:** Fill in the missing code to create a publisher in ROS 2:

```python
class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.________(
            String,
            'topic_name',
            10
        )
```

**Options:**
A. create_subscription
B. create_publisher
C. create_service
D. create_timer

**Correct Answer:** B (create_publisher)

**Explanation:**
The correct method to create a publisher in ROS 2 is `create_publisher()`. This method takes three arguments:
1. Message type (String in this case)
2. Topic name ('topic_name')
3. Queue size (10 - history depth for late-joining subscribers)

`create_subscription` would be used for creating a subscriber, not a publisher.

**Points:** 1

---

### Question 4 (Multiple Choice - Advanced)

**Question:** What happens when a publisher's queue is full and it tries to publish a new message?

**Options:**
A. The oldest message in the queue is dropped to make room for the new one
B. The new message is rejected and an error is logged
C. The publisher blocks until space is available in the queue
D. All messages in the queue are flushed and the new message is added

**Correct Answer:** A

**Explanation:**
When a publisher's queue (QoS history depth) is full, ROS 2 implements a "keep last N" policy by default. The oldest message is dropped to make room for the new message. This ensures that:
- Publishers never block on send (important for real-time systems)
- The most recent N messages are always available
- Late-joining subscribers get the most recent data

This behavior can be modified using QoS (Quality of Service) policies, such as changing to a "keep all" policy with a larger depth, but the default is "keep last N."

**Points:** 1

---

### Question 5 (Multiple Choice - Intermediate)

**Question:** Which ROS 2 command-line tool shows active topics and their message types?

**Options:**
A. ros2 node list
B. ros2 topic list -t
C. ros2 service list
D. ros2 param list

**Correct Answer:** B

**Explanation:**
The command `ros2 topic list -t` lists all active topics along with their message types. The `-t` flag adds type information.

- `ros2 node list`: Lists running nodes (not topics)
- `ros2 service list`: Lists active services (not topics)
- `ros2 param list`: Lists parameters (not topics)
- `ros2 topic list`: Lists topics without type information

Example output:
```
/topic_name [std_msgs/msg/String]
/rosout [rcl_interfaces/msg/Log]
```

**Points:** 1

---

### Question 6 (True/False - Beginner)

**Question:** True or False: Topics in ROS 2 guarantee message delivery to all subscribers.

**Options:**
A. True
B. False

**Correct Answer:** B (False)

**Explanation:**
This is false. ROS 2 topics do NOT guarantee message delivery by default. The delivery guarantees depend on the QoS (Quality of Service) settings:

- **Default (Best Effort):** Messages may be lost if network is congested or subscriber is slow
- **Reliable QoS:** System attempts to ensure delivery but may still lose messages under extreme conditions
- **Volatile Durability:** Late-joining subscribers miss earlier messages
- **Transient Local:** Late-joining subscribers can receive historical messages

For guaranteed delivery, you would need to use the Reliable QoS policy and appropriate durability settings, or consider using services/actions instead.

**Points:** 1

---

### Question 7 (Code Completion - Advanced)

**Question:** Complete the QoS profile configuration for a reliable publisher with history depth of 10:

```python
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

qos_profile = QoSProfile(
    reliability=ReliabilityPolicy.______,
    history=HistoryPolicy.KEEP_LAST,
    depth=10
)
```

**Options:**
A. BEST_EFFORT
B. RELIABLE
C. SYSTEM_DEFAULT
D. UNKNOWN

**Correct Answer:** B (RELIABLE)

**Explanation:**
For a reliable publisher that attempts to ensure message delivery, use `ReliabilityPolicy.RELIABLE`. The complete configuration:

- **RELIABLE:** Guarantees delivery attempts (retransmits if needed)
- **KEEP_LAST:** Keeps the last N messages (alternative: KEEP_ALL)
- **depth=10:** Maintains history of last 10 messages

`BEST_EFFORT` would be used for lossy but fast communication (like sensor data where latest value matters more than every value).

**Points:** 1

---

### Question 8 (Multiple Choice - Intermediate)

**Question:** What is the purpose of the timer in a typical ROS 2 publisher node?

**Options:**
A. To measure how long message publishing takes
B. To periodically publish messages at a fixed rate
C. To timeout and close the publisher after a certain duration
D. To synchronize multiple publishers

**Correct Answer:** B

**Explanation:**
In ROS 2, a timer is used to trigger a callback function at regular intervals. For publishers, this enables periodic message publication at a fixed rate.

Example:
```python
self.timer = self.create_timer(0.5, self.timer_callback)  # Calls callback every 0.5 seconds
```

This is commonly used for:
- Publishing sensor data at regular intervals (e.g., 10 Hz, 30 Hz)
- Heartbeat messages
- Status updates

The timer doesn't measure duration, timeout connections, or synchronize publishers - it simply triggers callbacks at specified intervals.

**Points:** 1

---

## Quiz Summary

**Total Questions:** 8
**Total Points:** 8
**Breakdown by Type:**
- Multiple Choice: 5 questions (62.5%)
- True/False: 2 questions (25%)
- Code Completion: 1 question (12.5%)

**Breakdown by Difficulty:**
- Beginner: 2 questions (25%)
- Intermediate: 5 questions (62.5%)
- Advanced: 1 question (12.5%)

**Learning Objectives Covered:**
✅ Understand publish-subscribe pattern
✅ Create publishers and subscribers in Python
✅ Use ROS 2 command-line tools
✅ Configure QoS policies
✅ Handle message queues and timing

---

## How Students Interact

1. **View Quiz:** After reading Chapter 3, student clicks "Take Quiz"
2. **Answer Questions:** Student answers all 8 questions (one at a time or all together)
3. **Submit:** Student submits answers
4. **Immediate Feedback:**
   - Question 1: ✓ Correct! (+1 point)
   - Question 2: ✓ Correct! (+1 point)
   - Question 3: ✗ Incorrect. The correct answer is B. [Shows explanation]
   - ... (continues for all questions)
5. **Final Score:** 7/8 (87.5%) - PASSED ✓
6. **Progress Saved:** Score recorded in user profile

---

## Database Storage

This quiz data is stored as:

**Quiz Table:**
```sql
id: uuid
chapter_id: 'chapter-03-ros2-topics'
title: 'ROS 2 Topics Quiz'
passing_score: 70.0
created_at: timestamp
```

**Quiz Questions Table (8 rows):**
```sql
id: uuid
quiz_id: [quiz uuid]
order_index: 0-7
question_text: [full question]
question_type: 'multiple_choice' | 'true_false' | 'code_completion'
options: ["A", "B", "C", "D"] (JSONB)
correct_answer: "B"
explanation: [full explanation]
difficulty: 'beginner' | 'intermediate' | 'advanced'
points: 1
```

**User Attempt (when student takes quiz):**
```sql
id: uuid
user_id: [user uuid]
quiz_id: [quiz uuid]
score: 87.5
points_earned: 7
total_points: 8
passed: true
started_at: timestamp
completed_at: timestamp
```

**User Responses (8 rows per attempt):**
```sql
id: uuid
attempt_id: [attempt uuid]
question_id: [question uuid]
user_answer: "B"
is_correct: true
points_awarded: 1
answered_at: timestamp
```

---

This structure enables:
- ✅ Multiple quiz attempts per user
- ✅ Detailed analytics (which questions are hardest)
- ✅ Progress tracking (completion percentage)
- ✅ Skill assessment (performance by difficulty level)
- ✅ Adaptive learning (skip beginner questions for advanced users)
