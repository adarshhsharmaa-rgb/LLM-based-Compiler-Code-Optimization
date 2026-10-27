// category: nested  (real program 005)
// Codeforces submission 20824865, problem 622/B, GNU C++, 2016-09-22
// https://codeforces.com/contest/622/submission/20824865
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>

using namespace std;



int main()

{

    int hh,mm,a,cur;

    scanf("%d:%d%d",&hh,&mm,&a);

    cur=(mm+hh*60)+a;

    hh=(cur/60)%24;

    mm=cur%60;

    printf("%02d:%02d\n",hh,mm);



}
