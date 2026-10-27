// category: repeated_expr  (real program 033)
// Codeforces submission 31084872, problem 869/B, GNU C++11, 2017-10-06
// https://codeforces.com/contest/869/submission/31084872
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
long long a,b;
int main(){
//	freopen("cf.in","r",stdin);
	scanf("%I64d%I64d",&a,&b);
	if (b-a>=5){printf("0");return 0;} long long ans=1;
	for (long long i=a+1;i<=b;++i) ans=ans*i%10;
	printf("%d",ans%10);return 0;
	if (a==0){
		if (b>=5){
			printf("0");return 0;
		}int ans=1;
		for (int i=1;i<=b;++i) ans*=i;
		printf("%d",ans%10);return 0;
	}
	if (b-a>=10) {printf("0");return 0;}
	int a1=a%10,b1=b%10;
	if (b1<=a1) {printf("0");return 0;} ans=1;
	for (int i=a1+1;i<=b1;++i) ans*=i;
	printf("%d",ans%10);
	return 0;
}
