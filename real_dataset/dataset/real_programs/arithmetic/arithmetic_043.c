// category: arithmetic  (real program 043)
// Codeforces submission 18534635, problem 622/B, GNU C++, 2016-06-17
// https://codeforces.com/contest/622/submission/18534635
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
int main(){
    int h,m;
    scanf("%d:%d",&h,&m);
    int a;
    scanf("%d",&a);
    m += a;
    h += m/60;
    m %= 60;
    h %= 24;
    printf("%02d:%02d",h,m);
    return 0;
}
