// category: arithmetic  (real program 052)
// Codeforces submission 18225619, problem 622/B, GNU C++, 2016-06-03
// https://codeforces.com/contest/622/submission/18225619
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;
int main()
{
	int h,  m,  a;
	scanf("%d:%d%d",&h, &m, &a);
	m += a;
    h += m / 60;
    m %= 60;
    h %= 24;
	printf("%02d:%02d\n",h,m);


}
