// category: arithmetic  (real program 045)
// Codeforces submission 20767451, problem 678/A, GNU C++11, 2016-09-20
// https://codeforces.com/contest/678/submission/20767451
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

#include<string.h>

#include<cmath>

#include<iostream>

using namespace std;

int main()

{

    int n,k,w;

    scanf("%d%d",&n,&k);

    w=n/k+1;

    printf("%d\n",w*k);

}
