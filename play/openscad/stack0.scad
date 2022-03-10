
//$fa = 1;
//$fs = 0.4;

for ( x= [1:1:10] ) {

    color(c = rands(0,255,3)/255 )
    translate([0,0,30-3*x])
    rotate([0,0,x*15+5])
    cylinder(h=rands(3,3,1)[0],r =4*x+1, center=!true, $fn=rands(8,9,1)[0]);
}