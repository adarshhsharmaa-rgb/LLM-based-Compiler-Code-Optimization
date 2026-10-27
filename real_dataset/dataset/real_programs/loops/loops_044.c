// category: loops  (real program 044)
// Codeforces submission 20994783, problem 579/A, GNU C, 2016-09-29
// https://codeforces.com/contest/579/submission/20994783
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
/*

 * CodeForces

 * Problem 579 A

 * MinGW/C

 */



#include <stdio.h>



int main()

{

  unsigned int bacterias;  // x

  unsigned int days = 0;



  scanf("%u", &bacterias);



  while (bacterias) {

    days += bacterias%2;

    bacterias /= 2;

  }



  printf("%u", days);



  return 0;

}
