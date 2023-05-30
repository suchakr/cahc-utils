// synthesize a layout as list of 10 non overlaping named rectangles [animal, width, height, x, y] where x,y, width, height are random numbers between 10 and 50
function random(n) = rands(10,100,1)[0];
function rand2(n1,n2) = round(rands(n1,n2,1)[0]);

layout = [
    ["chimpanzee", 10 + random(40), 10 + random(40), 10 + random(40), 10 + random(40)],
    ["elephant", 10 + random(40), 10 + random(40), 10 + random(40), 10 + random(40)],
    ["gazelle", 10 + random(40), 10 + random(40), 10 + random(40), 10 + random(40)],
    ["giraffe", 10 + random(40), 10 + random(40), 10 + random(40), 10 + random(40)],
    ["gorilla", 10 + random(40), 10 + random(40), 10 + random(40), 10 + random(40)],
    ["hippo", 10 + random(40), 10 + random(40), 10 + random(40), 10 + random(40)],
    ["kangaroo", 10 + random(40), 10 + random(40), 10 + random(40), 10 + random(40)],
    ["lion", 10 + random(40), 10 + random(40), 10 + random(40), 10 + random(40)],
    ["monkey", 10 + random(40), 10 + random(40), 10 + random(40), 10 + random(40)],
    ["rhino", 10 + random(40), 10 + random(40), 10 + random(40), 10 + random(40)],
    ["zebra", 10 + random(40), 10 + random(40), 10 + random(40), 10 + random(40)],
];

new_layout = [ for (idx = [0: len(layout)]) let (elem=layout[idx]) 
    [elem[0], 
    rand2(10,50), 
    rand2(10,50), 
    rand2((idx+3)*10, (idx+5)*10), 
    rand2((idx+1)*10, (idx+3)*10), 
    ]
];

echo(new_layout[0:3])


for (elem = new_layout) {
    translate([elem[3], elem[4], 0]) scale(.5) color("Red") linear_extrude(.1) text(elem[0]);
    translate([elem[3], elem[4], 0]) color("Yellow", 0.3) linear_extrude(1) square(elem[1]);

}