// category: mixed  (real program 013)
// Codeforces submission 18418594, problem 678/B, GNU C++11, 2016-06-13
// https://codeforces.com/contest/678/submission/18418594
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main(){
    int n;
    int isLeap=0;
    scanf("%d",&n);
    if(n%4!=0) isLeap=0;
    else if(n%100!=0) isLeap=1;
    else if(n%400!=0) isLeap=0;
    else isLeap=1;
    int day=0;

    //printf("leap = %d\n",isLeap);
    int p=n+1;
    for(;p<1000000;p++){
        int sLeap=0;
        if(p%4!=0) sLeap=0;
        else if(p%100!=0) sLeap=1;
        else if(p%400!=0) sLeap=0;
        else sLeap=1;
        if(sLeap) day+=366;
        else day+=365;
        day%=7;
        if(isLeap==sLeap){
            if(day==0)
            {
                printf("%d",p);
                return 0;
            }
        }
    }
}
