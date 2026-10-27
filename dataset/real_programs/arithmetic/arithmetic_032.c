// category: arithmetic  (real program 032)
// Codeforces submission 19309886, problem 622/B, GNU C++11, 2016-07-21
// https://codeforces.com/contest/622/submission/19309886
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>

#define mx 200001

#define mp make_pair



using namespace std;





int main()

{

    //freopen("in.txt","r",stdin);

  //  freopen("out.txt","w",stdout);

    int i,j,t,m,p,q,n;

    scanf("%d:%d",&m,&n);

    scanf("%d",&t);

    n += t;

    m += n/60;

    n%=60;

    m%=24;

    printf("%02d:%02d\n",m,n);

    return 0;

}
