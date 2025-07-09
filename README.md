# ENGMT280-Smart-Self-Parking-Vehicle
ENGMT280/ENGEE281 – 25B
Smart Self-parking Vehicle – Design Rules
A scaled version of a typical car park layout will be setup in D.2.03 and C.1.12 (eventually). So
please make sure to feel free to switch lab spaces during the later half of the trimester to have a
go at testing your systems on the track. Below are the design requirements and design constraints
that needs to met by the Smart self-parking vehicle (SSV) you design, while meeting the event
regulations.
Fig. 1(top). Arena for the SSV showing the starting point and the parking bays and (bottom)
Colored tiles placed at the parking bay’s rear wall and parking sensors to check successful vehicle
parking.
ENGMT280/ENGEE281 – 25B
1. Your SAV, once ‘started’, should be able to complete the task autonomously – i.e., no user
inputs from any sort of wired or wireless communication sources once the SSV starts to move.
2. The only form of external communication once your SSV starts is the camera feed going
between the SSV and your laptop/pc for image processing and the processed image’s info
being sent back to the SSV.
3. The SSV, before it’s switched ‘on’, should be completely within the starting area of the arena
(highlighted by the engraved box along the bottom part of the arena in Fig 1(top))
4. There is no restriction for which side can be chosen to start the SSV from as the arena is
symmetric along the vertical axis as seen from Fig 1 (top)’s orientation. The SSV design team
can choose their preferred starting side. If starting from the left-hand side, the SSV needs to
reverse while steering left into parking position and if starting from the right-hand side, the
SSV needs to reverse while steering right back into the parking bay.
5. There will be a reference tile after the starting point where the reference-coloured tile will
be placed that indicates the color of the parking bay that the SSV can park at.
6. The SSV needs to be able to travel along the parking area’s length while checking for available
spots and simultaneously check if that available spot is indeed a valid parking spot.
7. The reference color tile that the SSV needs to scan will be bicolored or single colored
depending on the event.
8. A bi-colored tile indicates that the 2 different spots the SSV should park at in sequence. For
instance if the reference tile is half red and half yellow, the SSV should park in both spots one
after the other in any order.
9. As a minimum requirement, the SSV should atleast be able to park at a single spot (teams can
request a single-colored tile if that’s all they manage to scan and park at). However, marks
will be awarded accordingly.
10. The scoring sheet will be made available on Moodle near the second half of the trimester.
11. The SSV can in no way cause any damage to any part of the arena including the dummy car
models placed in the parked spots.
12. The overall dimensional and dynamic constraints for the SSV are given below
a. Max Length of SSV – 180 mm
b. Max width of SSV – 80 mm
c. Max height of SSV – 75 mm
d. Absolute wheelbase of the SSV – 120 mm
e. The minimum turning radius for the SSV is – 245.346096 mm (represents the half of
the diametrical distance between the outer wheels of the rear axle of the SSV, while
making an exact 180° turn).
f. The SSV shall not have a differential
drive arrangement (not to be confused
with the use of differential gearbox)
where one wheel is driven intentionally
at a rate different from the other wheel
on the same axle that causes the chassis
to pivot with a sharper turning radius
(see Fig 2 for an example of differential
drive robot) Fig.2. Example of a differential drive
robot (which is not allowed)
ENGMT280/ENGEE281 – 25B
g. If the use of some standard parts causes the width of the SSV to be slightly higher than
the allowed SSV width, the teaching team may allow it.
13. All the colored tiles and the reference tile will only be placed after the SSV starts moving.
14. The order of colours tiles placed in the slots will be at random, and their orders will be
changed between each team’s runs.
15. The reference-colored tile will be placed before the SSV reaches the location.
16. The SSVs needs to stop within the correctly identiϐied parking bay’s engraved area and should
not bump the rear walls/colored tiles.
Fig. 2. Rendering showing what the dummy car placements will be like
17. Dummy model cars will also be placed at random creating randomized open parking bays in
the arena.
18. The dummy model cars will not have the same color as the colored tiles that would be
randomly placed to avoid ambiguity.
19. If the randomly chosen reference-color tile has a color that already has the dummy model
cars creating a situation where no valid parking bays are present, the SSV should continue
forward and come to a safe stop within the engraved area opposite to the starting spot.
20. Apart from the batteries provided, no other energy sources can be added to the SSV.
Components like elastic bands and light springs will be considered on a case-by-case basis.
(Make sure to consult before design decisions are made if using such energy storage devices).
21. All SSVs will be inspected to ensure unauthorized items are not present on the system and
they completely comply with all the dimensional and dynamic constraints.
22. SAVs considered unsafe to the users/ spectators/university buildings etc., will be disqualiϐied
at the discretion of the teaching team. Take care to consider H&S risk elements such as sharp
edges, ϐinger traps, electrical shorts, etc., and address them appropriately.
23. A list of available materials will be made available on Moodle under ‘design project resources’
section. Any speciϐic equipment if needed, needs to have prior permission obtained.
24. Under the discretion of the teaching team, 3D printing of parts may be allowed if its within a
volume of 3000 mm3 and merits the shape complexity that cannot be otherwise
manufactured using conventional fabrication approach.
ENGMT280/ENGEE281 – 25B
25. As an optional part, the teams can obtain a vacuformed body shell similar to that of the
dummy model car to put over your design. As such, the teams design should ensure all
electronics are within this envelope. Cut outs can be made on the vacuformed body shell to
allow for uninterrupted operation of any sensors.
26. YOUR SSV SHOULD BE CAPABLE OF ADAPTING TO THE CHANGING LIGHTING CONDITIONS
THROUGHOUT THE DAY ACROSS THE TRIMESTER. Any complaints that the lighting is too
harsh or varying will not be tolerated.
27. You will be given 3 tries to ϐinish your run and the best time of the three runs will be taken
for ϐinal grading.
28. If you have any queries on a speciϐic rule, please reach out for clariϐication. Do not assume
your own interpretation of a rule to be correct and have that as the deciding factor for any
design decisions made if there is any ambiguity in a rule.
Rule updates since ϐirst upload
