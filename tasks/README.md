# RoCo-BrickAssembly Task Definitions

## 🤺 Tasks

The Brick Assembly track features **two distinct evaluation tasks**. While all tasks require a solid grasp of physics and dexterous manipulation, the required reasoning capability progressively increases with each task. Initial setups are provided for all tasks to ensure an equal and standardized evaluation.

### Task 1. Step Assembly
This task tests the agent's ability to perform a single-step assembly (e.g., successfully placing a single brick at a target location).

#### **Input**: 

* `structure_start.json`: The initial assembly structure.
* Image renderings of the initial assembly structure from 30 different viewpoints.
* `structure_goal.json`: The goal assembly structure.
* Image renderings of the goal assembly structure from 30 different viewpoints.

#### **Evaluation Metric**: 

Pass/Fail. The agent receives **1 point** for successfully achieving the goal structure, and 0 points otherwise.

#### **Example**: 
* `structure_start.json`: 
```
{
    "1": {
        "x": 0,
        "y": 0,
        "z": 0,
        "ori": 0,
        "brick_id": 2,
        "color": "Red"
    }
}
``` 
* Initial assembly renderings.
<p
  align="center"
  style="
    display:grid;
    grid-template-columns:repeat(15, auto);
    gap:2px;
    justify-content:center;
  "
>
  <img src="type1/example1/start/frame_0001.png" width="100">
  <img src="type1/example1/start/frame_0002.png" width="100">
  <img src="type1/example1/start/frame_0003.png" width="100">
  <img src="type1/example1/start/frame_0004.png" width="100">
  <img src="type1/example1/start/frame_0005.png" width="100">
  <img src="type1/example1/start/frame_0006.png" width="100">
  <img src="type1/example1/start/frame_0007.png" width="100">
  <img src="type1/example1/start/frame_0008.png" width="100">
  <img src="type1/example1/start/frame_0009.png" width="100">
  <img src="type1/example1/start/frame_0010.png" width="100">
  <img src="type1/example1/start/frame_0011.png" width="100">
  <img src="type1/example1/start/frame_0012.png" width="100">
  <img src="type1/example1/start/frame_0013.png" width="100">
  <img src="type1/example1/start/frame_0014.png" width="100">
  <img src="type1/example1/start/frame_0015.png" width="100">
  <img src="type1/example1/start/frame_0016.png" width="100">
  <img src="type1/example1/start/frame_0017.png" width="100">
  <img src="type1/example1/start/frame_0018.png" width="100">
  <img src="type1/example1/start/frame_0019.png" width="100">
  <img src="type1/example1/start/frame_0020.png" width="100">
  <img src="type1/example1/start/frame_0021.png" width="100">
  <img src="type1/example1/start/frame_0022.png" width="100">
  <img src="type1/example1/start/frame_0023.png" width="100">
  <img src="type1/example1/start/frame_0024.png" width="100">
  <img src="type1/example1/start/frame_0025.png" width="100">
  <img src="type1/example1/start/frame_0026.png" width="100">
  <img src="type1/example1/start/frame_0027.png" width="100">
  <img src="type1/example1/start/frame_0028.png" width="100">
  <img src="type1/example1/start/frame_0029.png" width="100">
  <img src="type1/example1/start/frame_0030.png" width="100">
</p>

* `structure_goal.json`: 
```
{
    "1": {
        "x": 0,
        "y": 0,
        "z": 0,
        "ori": 0,
        "brick_id": 2,
        "color": "Red"
    },
    "2": {
        "x": 0,
        "y": 0,
        "z": 1,
        "ori": 0,
        "brick_id": 2,
        "color": "Blue
    }
}
``` 
* Goal assembly renderings.
<p
  align="center"
  style="
    display:grid;
    grid-template-columns:repeat(15, auto);
    gap:2px;
    justify-content:center;
  "
>
  <img src="type1/example1/goal/frame_0001.png" width="100">
  <img src="type1/example1/goal/frame_0002.png" width="100">
  <img src="type1/example1/goal/frame_0003.png" width="100">
  <img src="type1/example1/goal/frame_0004.png" width="100">
  <img src="type1/example1/goal/frame_0005.png" width="100">
  <img src="type1/example1/goal/frame_0006.png" width="100">
  <img src="type1/example1/goal/frame_0007.png" width="100">
  <img src="type1/example1/goal/frame_0008.png" width="100">
  <img src="type1/example1/goal/frame_0009.png" width="100">
  <img src="type1/example1/goal/frame_0010.png" width="100">
  <img src="type1/example1/goal/frame_0011.png" width="100">
  <img src="type1/example1/goal/frame_0012.png" width="100">
  <img src="type1/example1/goal/frame_0013.png" width="100">
  <img src="type1/example1/goal/frame_0014.png" width="100">
  <img src="type1/example1/goal/frame_0015.png" width="100">
  <img src="type1/example1/goal/frame_0016.png" width="100">
  <img src="type1/example1/goal/frame_0017.png" width="100">
  <img src="type1/example1/goal/frame_0018.png" width="100">
  <img src="type1/example1/goal/frame_0019.png" width="100">
  <img src="type1/example1/goal/frame_0020.png" width="100">
  <img src="type1/example1/goal/frame_0021.png" width="100">
  <img src="type1/example1/goal/frame_0022.png" width="100">
  <img src="type1/example1/goal/frame_0023.png" width="100">
  <img src="type1/example1/goal/frame_0024.png" width="100">
  <img src="type1/example1/goal/frame_0025.png" width="100">
  <img src="type1/example1/goal/frame_0026.png" width="100">
  <img src="type1/example1/goal/frame_0027.png" width="100">
  <img src="type1/example1/goal/frame_0028.png" width="100">
  <img src="type1/example1/goal/frame_0029.png" width="100">
  <img src="type1/example1/goal/frame_0030.png" width="100">
</p>

* Example Execution

<div
  align="center"
  style="
    display:flex;
    justify-content:center;
    gap:50px;
    flex-wrap:nowrap;
  "
>

  <figure style="text-align:center;">
    <img
      src="type1/example1/step_success.gif"
      style="height:150px; width:auto;"
    >
    <figcaption><b>Successful Step Assembly</b></figcaption>
  </figure>

  <figure style="text-align:center;">
    <img
      src="type1/example1/step_fail.gif"
      style="height:150px; width:auto;"
    >
    <figcaption><b>Failed Step Assembly</b></figcaption>
  </figure>
</div>


### Task 2. Sequence Assembly
This task requires the agent to assemble a goal structure from scratch. The final structural layout is provided, but no step-by-step guidance is given. The agent must reason and plan the assembly sequence accordingly.

#### **Input**: 

* `structure.json`: The goal assembly structure.
* Image renderings of the goal assembly structure from 30 different viewpoints.


#### **Evaluation Metric**: 

We compare the assembled structure against the goal structure. The score is calculated as the number of correctly assembled bricks.

#### **Example**: 

* `structure.json`: 
```
{
    "1": {
        "x": 0,
        "y": 0,
        "z": 0,
        "ori": 0,
        "brick_id": 2,
        "color": "Red"
    },
    "2": {
        "x": 0,
        "y": 0,
        "z": 1,
        "ori": 0,
        "brick_id": 2,
        "color": "Blue
    }
}
``` 
* Goal assembly renderings.
<p
  align="center"
  style="
    display:grid;
    grid-template-columns:repeat(15, auto);
    gap:2px;
    justify-content:center;
  "
>
  <img src="type2/example1/frame_0001.png" width="100">
  <img src="type2/example1/frame_0002.png" width="100">
  <img src="type2/example1/frame_0003.png" width="100">
  <img src="type2/example1/frame_0004.png" width="100">
  <img src="type2/example1/frame_0005.png" width="100">
  <img src="type2/example1/frame_0006.png" width="100">
  <img src="type2/example1/frame_0007.png" width="100">
  <img src="type2/example1/frame_0008.png" width="100">
  <img src="type2/example1/frame_0009.png" width="100">
  <img src="type2/example1/frame_0010.png" width="100">
  <img src="type2/example1/frame_0011.png" width="100">
  <img src="type2/example1/frame_0012.png" width="100">
  <img src="type2/example1/frame_0013.png" width="100">
  <img src="type2/example1/frame_0014.png" width="100">
  <img src="type2/example1/frame_0015.png" width="100">
  <img src="type2/example1/frame_0016.png" width="100">
  <img src="type2/example1/frame_0017.png" width="100">
  <img src="type2/example1/frame_0018.png" width="100">
  <img src="type2/example1/frame_0019.png" width="100">
  <img src="type2/example1/frame_0020.png" width="100">
  <img src="type2/example1/frame_0021.png" width="100">
  <img src="type2/example1/frame_0022.png" width="100">
  <img src="type2/example1/frame_0023.png" width="100">
  <img src="type2/example1/frame_0024.png" width="100">
  <img src="type2/example1/frame_0025.png" width="100">
  <img src="type2/example1/frame_0026.png" width="100">
  <img src="type2/example1/frame_0027.png" width="100">
  <img src="type2/example1/frame_0028.png" width="100">
  <img src="type2/example1/frame_0029.png" width="100">
  <img src="type2/example1/frame_0030.png" width="100">
</p>

* Successful Execution

<div
  align="center"
  style="
    display:flex;
    justify-content:center;
    gap:50px;
    flex-wrap:nowrap;
  "
>

  <figure style="text-align:center;">
    <img
      src="type2/example1/sequence_success.gif"
      style="height:150px; width:auto;"
    >
    <figcaption><b>Successful Sequence Assembly</b></figcaption>
  </figure>

  <figure style="text-align:center;">
    <img
      src="type2/example1/sequence_fail.gif"
      style="height:150px; width:auto;"
    >
    <figcaption><b>Failed Sequence Assembly</b></figcaption>
  </figure>
</div>

---

## 🧭 Score

The **final score** for the Brick Assembly track will be calculated as 

`Final Score = (S1 + S2_1^2 + S2_2^2 + S_3^2 + ... + S_N^2)`

where S1 is the total score achieved by completing type-1 tasks and S2_i is the score by completing the i-th task in type-2 tasks.

The above example **successful** execution will receive a score of

```
S1 = 1
S2_1 = 2
Final Score = 1 + 2^2 = 5
```
The example **failed** execution will receive a score of

```
S1 = 0
S2_1 = 1
Final Score = 0 + 1^2 = 1
```

## 🧱 Brick Representation
We represent a brick assembly structure using a JSON dictionary. Each node represents a distinct brick in the structure with the following format:
```
"id": {
    brick_id,
    x,
    y,
    z,
    ori,
    color
    }
``` 
where `brick_id` denotes the brick type (definition can be found in [`config/lego_library.json`](../config/lego_library.json)), `x, y, z` are the brick relative position in the structure. `ori` is the brick orientation and `color` is the 
<a href="https://rebrickable.com/colors/"
   target="_blank"
   rel="noopener noreferrer"
   style="color:#ff6600; font-weight:bold; text-decoration:none;">
  color name
</a> 
indicating the color of the brick. In this challenge, we will have 7 types of bricks, including *1x2, 1x4, 1x6, 1x8, 2x2, 2x4, and 2x6*, with different colors.

