

$fa = 1;
$fs = 0.4;

scale ( [1.2, 1, 1] ) {
base_height = 5;
top_height = 8;
color("blue")
    scale([1.2,1,1])
    cube([60,20,base_height], center=true, alpha=0.2);

color("yellow") 
    scale([1,1,1]) 
    translate([5,0,base_height-.01]) 
    cube ([30,20,top_height] , center=true);
}

wheel_radius = 12;
 for (w = [ [1,1], [1,-1], [-1,1], [-1,-1]]) { // wheel
     color("orange", alpha=0.8) 
     translate([w[0]*20,w[1]*15,0]) 
     rotate([90,0,(-w[0]+1)*-5]) 
     cylinder(h=3,r=wheel_radius +0*rands(1,5,1)[0], center=true);
 }
 
  for (a = [1,-1]) { // axel
     color("red", alpha=0.8) 
     translate([a*20,0,0]) 
     rotate([90,0,0]) 
     cylinder(h=30,r=3, center=true);
 }
 