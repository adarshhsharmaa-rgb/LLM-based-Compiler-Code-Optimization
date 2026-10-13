// category: dead_code  (real program 038)
// Codeforces submission 21209787, problem 622/A, GNU C, 2016-10-05
// https://codeforces.com/contest/622/submission/21209787
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

#include<stdlib.h>

#include<math.h>

#include<string.h>

#include<time.h>

#include<ctype.h>

#include<limits.h>

#define eps 1e-9

#define ll long long int 

#define N 500500

int main(){

   ll a;

   scanf("%lld",&a);

   ll s=0;

   ll numb=s;ll inc=0;

   while(s<a){

      s+=(inc+1);

      inc++;

   }

   while(s>a){

      s--;

      inc--;

   }

   printf("%lld",inc);

}
