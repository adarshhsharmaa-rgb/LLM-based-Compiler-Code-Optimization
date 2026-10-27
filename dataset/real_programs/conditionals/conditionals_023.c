// category: conditionals  (real program 023)
// Codeforces submission 36950501, problem 922/A, GNU C++, 2018-04-04
// https://codeforces.com/contest/922/submission/36950501
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
#include<iostream>
#include<string>
#include<cstring>
#include<cmath>
using namespace std;

int main()
{
 long long int x, y;
 scanf("%lld%lld", &x, &y);
 y--;
 if (x<y || y<0 || (y == 0 && x>0)) 
 { 
  printf("No\n"); 
  return 0; 
 }
 if ((x - y) % 2 == 0)
 {
  printf("Yes\n");
 }
 else
 {
  printf("No\n");
 }
 return 0;
}
