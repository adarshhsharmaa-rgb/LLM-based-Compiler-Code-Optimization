// category: dead_code  (real program 017)
// Codeforces submission 34294873, problem 910/B, GNU C++, 2018-01-19
// https://codeforces.com/contest/910/submission/34294873
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
int main()
{
 int n,a,b;
 int t;
 int sum=0;
 int y=0;
 scanf("%d%d%d",&n,&a,&b);
 if(n>=4*a+2*b)  // 1 kuai
 {
  printf("1\n");
  return 0;
 }
 else if((n>=b*2&&n>=4*a)||(n>=b+2*a)) // 2 kuai  2b,4a; 1b2a,1b2a;  
 {
  printf("2\n");
  return 0;
 }
 else if((n>=2*b&&n>=2*a)||(n>=b+a&&n>=2*a)||(n>=b&&n>=4*a))  // 3 kuai  2b,2a,2a;  1b2a,1b1a,1a;  1b1a,1b1a,2a;  1b3a,1b,1a;    
 {
  printf("3\n");
  return 0;
 }
 else if((n>=2*b&&n>=2*a)||(n>=b+2*a)||(n>=b+a)||(n>=b&&n>=2*a))  // 4 kuai  2b,2a,a,a;  1b2a,1b,a,a;  1b1a,1b1a,a,a;  1b1a,1b,2a,1a  ;1b,1b,
 {
  printf("4\n");
  return 0;
 }
 else if(/*n>=a+b||n>=2*b*/(n>=2*b&&n>=a)||(n>=a+b)||(n>=2*a&&n>=b))  //5kuai 1b1a,1b,a,a,a;  2b;2a
 {
  printf("5\n");
  return 0;
 }
 else
 {
  printf("6\n");
  return 0;
 }
}
