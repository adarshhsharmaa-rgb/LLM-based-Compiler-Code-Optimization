// category: dead_code  (real program 032)
// Codeforces submission 20880921, problem 492/A, GNU C, 2016-09-24
// https://codeforces.com/contest/492/submission/20880921
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>



int main()

{

    int in,out,sum=0;

    scanf("%d",&in);

    for (out = 1; (out*(out+1)*(out+2))/6 <= in ; out++);

    printf("%d",out-1);

}
