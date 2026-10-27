// category: mixed  (real program 020)
// Codeforces submission 20624386, problem 110/A, GNU C, 2016-09-14
// https://codeforces.com/contest/110/submission/20624386
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main()

{



long long int n,i,last,count=0;

scanf("%lld",&n);

for(i=0;n>0;i++)

{

last=(n%10);

if(last==7 || last==4)

count++;

n=n/10;

}

if(count==7 ||  count==4)

printf("YES");

else

printf("NO");



return 0;

}
