// category: repeated_expr  (real program 032)
// Codeforces submission 633815, problem 108/A, GNU C++, 2011-08-23
// https://codeforces.com/contest/108/submission/633815
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
#include<cstring>
#include<cstdlib>
#include<cmath>

int main()
{
    int a,b;
    scanf("%d%*c%d",&a,&b);
    if(a<=4)
    {
	if(b<a*10)
	    printf("0%d:%d0\n",a,a);
	else
	    printf("0%d:%d0\n",a+1,a+1);
    }
    else if(a==5 && b<50)
	printf("05:50\n");
    else if(a>=5 && a<=9)
	printf("10:01\n");
    else if(a>=10 && a<=14)
    {
	if(b<((a%10)*10+a/10))
	    printf("%d:%d%d\n",a,a%10,a/10);
	else
	    printf("%d:%d%d\n",a+1,(a+1)%10,(a+1)/10);
    }
    else if(a==15 && b<51)
	printf("15:51\n");
    else if(a>=15 && a<=19)
	printf("20:02\n");
    else if(a>=20 && a<=22)
    {
	if(b<((a%10)*10+a/10))
	    printf("%d:%d%d\n",a,a%10,a/10);
	else
	    printf("%d:%d%d\n",a+1,(a+1)%10,(a+1)/10);
    }
    else if(a==23 && b<32)
	printf("23:32\n");
    else
	printf("00:00\n");
    return 0;
}
