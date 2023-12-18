// module trapezoid(base1 = 64, base2 = 48, height = 96) {
//     // Points
//     A = [-base1/2, 0];
//     B = [base1/2, 0];
//     C = [base2/2, height];
//     D = [-base2/2, height];

//     // Faces
//     polygon([A, B, C, D]);

//     // Edges
//     for (i = [0:3]) {
//         line(A[i], B[i]);
//         line(B[i], C[i]);
//         line(C[i], D[i]);
//         line(D[i], A[i]);
//     }
// }

// // Render the trapezoid
// trapezoid();


module trapezoid() {
  // Define the dimensions of the trapezoid
  a = 48; // length of AB
  b = 64; // length of CD
  h = 96; // separation between AB and CD
  d = (a + b) / 2; // average length of AB and CD

  // Define the points of the trapezoid
  A = [0, 0];
  B = [a, 0];
  C = [a + h, d];
  D = [h, d];

  // Create the trapezoid with linear_extrude
  linear_extrude(height = 1) {
    polygon(points = [A, B, C, D, A]);
  }
}

// Generate the trapezoid
trapezoid();
