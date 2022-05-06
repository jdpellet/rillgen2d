#include<stdio.h>
#include<stdlib.h>
#include<math.h>

#define FREE_ARG char*
#define NR_END 1
#define stacksize 100000000
#define PI 3.1415926535897932
#define PIover4 0.78539816339744800
#define sqrt2 1.414213562373
#define oneoversqrt2 0.707106781186
#define large 1.e12
#define small 1.e-12
#define mfdweight 1.1

long count,*topovecind,*flatis,*flatjs,*iup,*idown,*jup,*jdown,lattice_size_x,lattice_size_y,ic,jc;
int flagfordynamicmode,numberofraindata,numberofraingages,**closestgage,expansion,smoothinglength,numberofdatapoints,flagforrainrasters,flagforequation,flagfordynamicmode,flagformask,flagforslope,flagford50,flagfortaucsoilandveg,flagforrain,flagforcu,flagforthickness,flagforrockcover,**mask;
float rillwidth,nodatavalue,oneoverdeltax,durationofdata,timestep,ulx,uly,*raingagex,*raingagey,**dischargewithoutrain,**sinofslope,rillwidthcoefficient,rillwidthexponent,dist,mindist,*rainvalues,durationofdata,minslope,**slopefactor,**rainl,**rain,**d50,**cu,**thickness,**rockcover,**taucsoilandveg,**tauwithoutrain,**topo,**slope,**area,flow1,flow2,flow3,flow4,flow5,flow6,flow7,flow8,*topovec,fillincrement,**inciseddepth,**f,**f2,slopex,slopey,deltax,yellowthreshold,rainfixed,b,c,d50fixed,rockcoverfixed,bulkdensity,timescaleofinterest,durationofdata,rillerodibility,tanangleofinternalfriction,taucsoilandvegfixed,**cosofslopeterm,**taucarmor;

void free_vector(float *v, long nl, long nh)
/* free a float vector allocated with vector() */
{
	free((FREE_ARG) (v+nl-NR_END));
}

void free_lvector(long *v, long nl, long nh)
/* free an unsigned long vector allocated with lvector() */
{
	free((FREE_ARG) (v+nl-NR_END));
}

void free_matrix(float **m, long nrl, long nrh, long ncl, long nch)
/* free a float matrix allocated by matrix() */
{
	free((FREE_ARG) (m[nrl]+ncl-NR_END));
	free((FREE_ARG) (m+nrl-NR_END));
}

void free_imatrix(int **m, long nrl, long nrh, long ncl, long nch)
/* free an int matrix allocated by imatrix() */
{
	free((FREE_ARG) (m[nrl]+ncl-NR_END));
	free((FREE_ARG) (m+nrl-NR_END));
}

long *lvector(long nl, long nh)
/* allocate an unsigned long vector with subscript range v[nl..nh] */
{
	long *v;

	v=(long *)malloc((size_t) ((nh-nl+1+NR_END)*sizeof(long)));
	return v-nl+NR_END;
}

float *vector(long nl, long nh)
/* allocate an int vector with subscript range v[nl..nh] */
{
        float *v;

        v=(float *)malloc((size_t) ((nh-nl+1+NR_END)*sizeof(float)));
        return v-nl+NR_END;
}

float **matrix(long nrl, long nrh, long ncl, long nch)
/* allocate a float matrix with subscript range m[nrl..nrh][ncl..nch] */
{
	long i, nrow=nrh-nrl+1,ncol=nch-ncl+1;
	float **m;

	/* allocate pointers to rows */
	m=(float **) malloc((size_t)((nrow+NR_END)*sizeof(float*)));
	m += NR_END;
	m -= nrl;

	/* allocate rows and set pointers to them */
	m[nrl]=(float *) malloc((size_t)((nrow*ncol+NR_END)*sizeof(float)));
	m[nrl] += NR_END;
	m[nrl] -= ncl;

	for(i=nrl+1;i<=nrh;i++) m[i]=m[i-1]+ncol;

	/* return pointer to array of pointers to rows */
	return m;
}

int **imatrix(long nrl, long nrh, long ncl, long nch)
/* allocate a float matrix with subscript range m[nrl..nrh][ncl..nch] */
{
	long i, nrow=nrh-nrl+1,ncol=nch-ncl+1;
	int **m;

	/* allocate pointers to rows */
	m=(int **) malloc((size_t)((nrow+NR_END)*sizeof(int*)));
	m += NR_END;
	m -= nrl;

	/* allocate rows and set pointers to them */
	m[nrl]=(int *) malloc((size_t)((nrow*ncol+NR_END)*sizeof(int)));
	m[nrl] += NR_END;
	m[nrl] -= ncl;

	for(i=nrl+1;i<=nrh;i++) m[i]=m[i-1]+ncol;

	/* return pointer to array of pointers to rows */
	return m;
}

#define SWAP(a,b) itemp=(a);(a)=(b);(b)=itemp;
#define M 7
#define NSTACK 100000

void indexx(long n, float arr[], long indx[])
{
	long i,indxt,ir=n,itemp,j,k,l=1,jstack=0,*istack;
	float a;
	
        istack=lvector(1,NSTACK);
        for (j=1;j<=n;j++) indx[j]=j;
        for (;;) {
                if (ir-l < M) {
                        for (j=l+1;j<=ir;j++) {
                                indxt=indx[j];
                                a=arr[indxt];
                                for (i=j-1;i>=1;i--) {
                                        if (arr[indx[i]] <= a) break;
                                        indx[i+1]=indx[i];
                                }
                                indx[i+1]=indxt;
                        }
                        if (jstack == 0) break;
                        ir=istack[jstack--];
                        l=istack[jstack--];
                } else {
                        k=(l+ir) >> 1;
                        SWAP(indx[k],indx[l+1]);
                        if (arr[indx[l+1]] > arr[indx[ir]]) {
                                SWAP(indx[l+1],indx[ir])
                        }
                        if (arr[indx[l]] > arr[indx[ir]]) {
                                SWAP(indx[l],indx[ir])
                        }
                        if (arr[indx[l+1]] > arr[indx[l]]) {
                                SWAP(indx[l+1],indx[l])
                        }
                        i=l+1;
                        j=ir;
                        indxt=indx[l];
                        a=arr[indxt];
                        for (;;) {
                                do i++; while (arr[indx[i]] < a);
                                do j--; while (arr[indx[j]] > a);
                                if (j < i) break;
                                SWAP(indx[i],indx[j])
                        }
                        indx[l]=indx[j];
                        indx[j]=indxt;
                        jstack += 2;
                        if (ir-i+1 >= j-l) {
                                istack[jstack]=ir;
                                istack[jstack-1]=i;
                                ir=j-1;
                        } else {
                                istack[jstack]=j-1;
                                istack[jstack-1]=l;
                                l=i;
                        }
                }
        }
        free_lvector(istack,1,NSTACK);
}
#undef M
#undef NSTACK
#undef SWAP

void setupgridneighbors()
{    long i,j;

     idown=lvector(1,lattice_size_x);
     iup=lvector(1,lattice_size_x);
     jup=lvector(1,lattice_size_y);
     jdown=lvector(1,lattice_size_y);
     for (i=1;i<=lattice_size_x;i++)
      {idown[i]=i-1;
       iup[i]=i+1;}
     idown[1]=1;
     iup[lattice_size_x]=lattice_size_x;
     for (j=1;j<=lattice_size_y;j++)
      {jdown[j]=j-1;
       jup[j]=j+1;}
     jdown[1]=1;
     jup[lattice_size_y]=lattice_size_y;
}

void mfdflowroute(i,j)
long i,j;
{    float tot;

     if ((mask[i][j]==1)&&(slope[i][j]>minslope)&&(i>1)&&(i<lattice_size_x)&&(j>1)&&(j<lattice_size_y))
	  {tot=0;
       if (topo[i][j]>topo[iup[i]][j]) tot+=pow(topo[i][j]-topo[iup[i]][j],mfdweight);
       if (topo[i][j]>topo[idown[i]][j]) tot+=pow(topo[i][j]-topo[idown[i]][j],mfdweight);
       if (topo[i][j]>topo[i][jup[j]]) tot+=pow(topo[i][j]-topo[i][jup[j]],mfdweight);
       if (topo[i][j]>topo[i][jdown[j]]) tot+=pow(topo[i][j]-topo[i][jdown[j]],mfdweight);
       if (topo[i][j]>topo[iup[i]][jup[j]]) tot+=pow((topo[i][j]-topo[iup[i]][jup[j]])*oneoversqrt2,mfdweight);
       if (topo[i][j]>topo[iup[i]][jdown[j]]) tot+=pow((topo[i][j]-topo[iup[i]][jdown[j]])*oneoversqrt2,mfdweight);
       if (topo[i][j]>topo[idown[i]][jup[j]]) tot+=pow((topo[i][j]-topo[idown[i]][jup[j]])*oneoversqrt2,mfdweight);
       if (topo[i][j]>topo[idown[i]][jdown[j]]) tot+=pow((topo[i][j]-topo[idown[i]][jdown[j]])*oneoversqrt2,mfdweight);
       if (topo[i][j]>topo[iup[i]][j]) flow1=pow(topo[i][j]-topo[iup[i]][j],mfdweight)/tot; else flow1=0;
       if (topo[i][j]>topo[idown[i]][j]) flow2=pow(topo[i][j]-topo[idown[i]][j],mfdweight)/tot; else flow2=0;
       if (topo[i][j]>topo[i][jup[j]]) flow3=pow(topo[i][j]-topo[i][jup[j]],mfdweight)/tot; else flow3=0;
       if (topo[i][j]>topo[i][jdown[j]]) flow4=pow(topo[i][j]-topo[i][jdown[j]],mfdweight)/tot; else flow4=0;
       if (topo[i][j]>topo[iup[i]][jup[j]]) flow5=pow((topo[i][j]-topo[iup[i]][jup[j]])*oneoversqrt2,mfdweight)/tot; else flow5=0;
       if (topo[i][j]>topo[iup[i]][jdown[j]]) flow6=pow((topo[i][j]-topo[iup[i]][jdown[j]])*oneoversqrt2,mfdweight)/tot; else flow6=0;
       if (topo[i][j]>topo[idown[i]][jup[j]]) flow7=pow((topo[i][j]-topo[idown[i]][jup[j]])*oneoversqrt2,mfdweight)/tot; else flow7=0;
       if (topo[i][j]>topo[idown[i]][jdown[j]]) flow8=pow((topo[i][j]-topo[idown[i]][jdown[j]])*oneoversqrt2,mfdweight)/tot; else flow8=0;
       area[iup[i]][j]+=area[i][j]*flow1;
       area[idown[i]][j]+=area[i][j]*flow2;
       area[i][jup[j]]+=area[i][j]*flow3;
       area[i][jdown[j]]+=area[i][j]*flow4;
       area[iup[i]][jup[j]]+=area[i][j]*flow5;
       area[iup[i]][jdown[j]]+=area[i][j]*flow6;
       area[idown[i]][jup[j]]+=area[i][j]*flow7;
       area[idown[i]][jdown[j]]+=area[i][j]*flow8;}
}

void push(i,j)
long i,j;
{  
	 count++;
     flatis[count]=i;
     flatjs[count]=j;
}

void pop()
{  
     ic=flatis[count];
     jc=flatjs[count];
	 count--;
}

void hydrologiccorrection()
{    long i,j;
     float max;

     printf("percent of hydrologic correction completed: ");
	 fflush(stdout);
	 count=stacksize;
	 while (count==stacksize)
	  {count=0;
       for (j=1;j<=lattice_size_y;j++)
	   {if (j%(lattice_size_y/10)==0) {printf("%ld ",10*j/(lattice_size_y/10));fflush(stdout);}
        for (i=1;i<=lattice_size_x;i++)
	     {push(i,j);
	      while (count>0) 
		   {pop();
		    max=topo[ic][jc];
            if (topo[iup[ic]][jc]<max) max=topo[iup[ic]][jc];
            if (topo[idown[ic]][jc]<max) max=topo[idown[ic]][jc];
            if (topo[ic][jup[jc]]<max) max=topo[ic][jup[jc]];
            if (topo[ic][jdown[jc]]<max) max=topo[ic][jdown[jc]];
	        if (topo[iup[ic]][jup[jc]]<max) max=topo[iup[ic]][jup[jc]];
            if (topo[idown[ic]][jdown[jc]]<max) max=topo[idown[ic]][jdown[jc]];
            if (topo[idown[ic]][jup[jc]]<max) max=topo[idown[ic]][jup[jc]];
            if (topo[iup[ic]][jdown[jc]]<max) max=topo[iup[ic]][jdown[jc]];
            if ((mask[ic][jc]==1)&&(topo[ic][jc]>0)&&(topo[ic][jc]<=max)&&(ic>1)&&(jc>1)&&(ic<lattice_size_x)&&(jc<lattice_size_y)&&(count<stacksize))
		     {topo[ic][jc]=max+fillincrement;
			  push(ic,jc);
			  push(iup[ic],jc);
			  push(idown[ic],jc);
			  push(ic,jup[jc]);
			  push(ic,jdown[jc]);
	          push(iup[ic],jup[jc]);
			  push(idown[ic],jdown[jc]);
			  push(idown[ic],jup[jc]);
	          push(iup[ic],jdown[jc]);}}}}}
}



void smoothslope()
{    long i,j,i2,j2,il,jl;
     int n,**countslope;
     float **sumslope;

	 sumslope=matrix(1,lattice_size_x,1,lattice_size_y);
	 countslope=imatrix(1,lattice_size_x,1,lattice_size_y);
	 for (j=1;j<=lattice_size_y;j++)
      for (i=1;i<=lattice_size_x;i++)
	   {sumslope[i][j]=0;
	    countslope[i][j]=0;}
	 j=smoothinglength/2;
     for (i=1;i<=lattice_size_x;i++)
	  for (j2=j-smoothinglength/2;j2<=j+smoothinglength/2;j2++)      
	   for (i2=i-smoothinglength/2;i2<=i+smoothinglength/2;i2++)
		{il=i;
	     jl=j;
		 if (i2<i) for (n=1;n<=i-i2;n++) il=idown[il]; else for (n=1;n<=i2-i;n++) il=iup[il];
	     if (j2<j) for (n=1;n<=j-j2;n++) jl=jdown[jl]; else for (n=1;n<=j2-j;n++) jl=jup[jl];
		 if (mask[il][jl]==1) {sumslope[i][j]+=slope[il][jl];countslope[i][j]++;}}
     j=lattice_size_y-smoothinglength/2;
     for (i=1;i<=lattice_size_x;i++)
	  for (j2=j-smoothinglength/2;j2<=j+smoothinglength/2;j2++)      
	   for (i2=i-smoothinglength/2;i2<=i+smoothinglength/2;i2++)
		{il=i;
	     jl=j;
		 if (i2<i) for (n=1;n<=i-i2;n++) il=idown[il]; else for (n=1;n<=i2-i;n++) il=iup[il];
	     if (j2<j) for (n=1;n<=j-j2;n++) jl=jdown[jl]; else for (n=1;n<=j2-j;n++) jl=jup[jl];
		 if (mask[il][jl]==1) {sumslope[i][j]+=slope[il][jl];countslope[i][j]++;}} 
     i=smoothinglength/2;
     for (j=1;j<=lattice_size_y;j++)
      for (j2=j-smoothinglength/2;j2<=j+smoothinglength/2;j2++)      
	   for (i2=i-smoothinglength/2;i2<=i+smoothinglength/2;i2++)
		{il=i;
	     jl=j;
		 if (i2<i) for (n=1;n<=i-i2;n++) il=idown[il]; else for (n=1;n<=i2-i;n++) il=iup[il];
	     if (j2<j) for (n=1;n<=j-j2;n++) jl=jdown[jl]; else for (n=1;n<=j2-j;n++) jl=jup[jl];
		 if (mask[il][jl]==1) {sumslope[i][j]+=slope[il][jl];countslope[i][j]++;}} 		 
     i=lattice_size_x-smoothinglength/2;
     for (j=1;j<=lattice_size_y;j++)
      for (j2=j-smoothinglength/2;j2<=j+smoothinglength/2;j2++)      
	   for (i2=i-smoothinglength/2;i2<=i+smoothinglength/2;i2++)
		{il=i;
	     jl=j;
		 if (i2<i) for (n=1;n<=i-i2;n++) il=idown[il]; else for (n=1;n<=i2-i;n++) il=iup[il];
	     if (j2<j) for (n=1;n<=j-j2;n++) jl=jdown[jl]; else for (n=1;n<=j2-j;n++) jl=jup[jl];
		 if (mask[il][jl]==1) {sumslope[i][j]+=slope[il][jl];countslope[i][j]++;}} 		 
	 for (j=smoothinglength/2+1;j<lattice_size_y-smoothinglength/2;j++)
	  {for (i=smoothinglength/2+1;i<lattice_size_x-smoothinglength/2;i++)  
	    {sumslope[i][j]=sumslope[idown[i]][j];
	     countslope[i][j]=countslope[idown[i]][j];
         for (j2=-smoothinglength/2;j2<=smoothinglength/2;j2++)
	      {if (mask[i-smoothinglength/2][j+j2]==1) {sumslope[i][j]-=slope[i-smoothinglength/2][j+j2];countslope[i][j]--;}
	       if (mask[i+smoothinglength/2][j+j2]==1) {sumslope[i][j]+=slope[i+smoothinglength/2][j+j2];countslope[i][j]++;}}}
	   i=smoothinglength/2+1;}
	 for (j=1;j<=lattice_size_y;j++)
      for (i=1;i<=lattice_size_x;i++)  
	   if (countslope[i][j]>(smoothinglength*smoothinglength/2)) slope[i][j]=sumslope[i][j]/countslope[i][j]; 
     free_matrix(sumslope,1,lattice_size_x,1,lattice_size_y);
	 free_imatrix(countslope,1,lattice_size_x,1,lattice_size_y);
}

void computecontributingarea()
{   long i,j,m;

	topovec=vector(1,lattice_size_x*lattice_size_y);
	topovecind=lvector(1,lattice_size_x*lattice_size_y);
	area=matrix(1,lattice_size_x,1,lattice_size_y);
	for (j=1;j<=lattice_size_y;j++)
     for (i=1;i<=lattice_size_x;i++)
	  {topovec[(j-1)*lattice_size_x+i]=topo[i][j];
	   if (mask[i][j]==1) area[i][j]=deltax*deltax; else area[i][j]=0;}
	indexx(lattice_size_x*lattice_size_y,topovec,topovecind);
	m=lattice_size_x*lattice_size_y+1;
	while (m>1)
	 {m--;
      i=(topovecind[m])%lattice_size_x;
      if (i==0) i=lattice_size_x;
      j=(topovecind[m])/lattice_size_x+1;
      if (i==lattice_size_x) j--;
	  mfdflowroute(i,j);}
    free_vector(topovec,1,lattice_size_x*lattice_size_y);
	free_lvector(topovecind,1,lattice_size_x*lattice_size_y);  
}

int main()
{
     FILE *fpin,*fp0,*fp1,*fp2,*fp3,*fp4,*fp5;
	 long i,j,m,n;
	 
	 fpin=fopen("./input.txt","r");
	 fp0=fopen("./topo.txt","r");
	 fp1=fopen("./f.txt","w");
	 fp2=fopen("./rills.ppm","w");
	 fp3=fopen("./tau.txt","w");
	 fscanf(fpin,"%d",&flagforequation);
	 fscanf(fpin,"%d",&flagfordynamicmode);
	 fscanf(fpin,"%d",&flagformask);
	 fscanf(fpin,"%d",&flagfortaucsoilandveg);
	 fscanf(fpin,"%d",&flagford50); 
	 fscanf(fpin,"%d",&flagforrockcover);
	 fscanf(fpin,"%f",&fillincrement);
	 fscanf(fpin,"%f",&minslope);  
	 fscanf(fpin,"%d",&expansion); 
	 fscanf(fpin,"%f",&yellowthreshold); 
	 fscanf(fpin,"%ld",&lattice_size_x);
	 fscanf(fpin,"%ld",&lattice_size_y);
	 fscanf(fpin,"%f",&deltax);
	 fscanf(fpin,"%f",&nodatavalue);
	 fscanf(fpin,"%d",&smoothinglength);
     fscanf(fpin,"%f",&rainfixed);	 
	 fscanf(fpin,"%f",&taucsoilandvegfixed);
	 fscanf(fpin,"%f",&d50fixed);
     fscanf(fpin,"%f",&rockcoverfixed);  
	 fscanf(fpin,"%f",&tanangleofinternalfriction); 
	 fscanf(fpin,"%f",&b);
	 fscanf(fpin,"%f",&c);
	 fscanf(fpin,"%f",&rillwidthcoefficient);
     fscanf(fpin,"%f",&rillwidthexponent);
	 fclose(fpin);
	 oneoverdeltax=1.0/deltax;
	 setupgridneighbors();
	 mask=imatrix(1,lattice_size_x,1,lattice_size_y);
	 topo=matrix(1,lattice_size_x,1,lattice_size_y);
	 slope=matrix(1,lattice_size_x,1,lattice_size_y);
	 flatis=lvector(1,stacksize);
	 flatjs=lvector(1,stacksize);
	 if (flagformask==0) 
	  {for (j=1;j<=lattice_size_y;j++)
	    for (i=1;i<=lattice_size_x;i++)
		 mask[i][j]=1;} 
	  else 
	   {fp4=fopen("./mask.txt","r");
        for (j=1;j<=lattice_size_y;j++)
	     for (i=1;i<=lattice_size_x;i++)
		  {fscanf(fp4,"%d",&mask[i][j]);
		   if (mask[i][j]>0) mask[i][j]=1;}
		fclose(fp4);}
	 for (j=1;j<=lattice_size_y;j++)
	  for (i=1;i<=lattice_size_x;i++)
	   {fscanf(fp0,"%f",&topo[i][j]);
	    if (topo[i][j]<=nodatavalue) mask[i][j]=0;}
	 for (j=1;j<=lattice_size_y;j++)
      for (i=1;i<=lattice_size_x;i++)
	   {slopex=topo[iup[i]][j]-topo[idown[i]][j];
        slopey=topo[i][jup[j]]-topo[i][jdown[j]];
	    if ((mask[i][j]==1)&&(mask[iup[i]][j]==1)&&(mask[idown[i]][j]==1)&&(mask[i][jup[j]]==1)&&(mask[i][jdown[j]]==1))
	     slope[i][j]=0.5*oneoverdeltax*sqrt(slopex*slopex+slopey*slopey);
	    else slope[i][j]=0;}
	 if (smoothinglength>1) smoothslope();
     hydrologiccorrection(); 
	 slopefactor=matrix(1,lattice_size_x,1,lattice_size_y);
	 sinofslope=matrix(1,lattice_size_x,1,lattice_size_y);
	 cosofslopeterm=matrix(1,lattice_size_x,1,lattice_size_y);
	 for (j=1;j<=lattice_size_y;j++)
      for (i=1;i<=lattice_size_x;i++)
	   {cosofslopeterm[i][j]=sqrt(9.81*cos(atan(slope[i][j])));
        sinofslope[i][j]=sin(atan(slope[i][j]));
        slopefactor[i][j]=sin(atan(slope[i][j]))/(cos(atan(slope[i][j]))*tanangleofinternalfriction-sin(atan(slope[i][j])));}
	 computecontributingarea();  
	 taucsoilandveg=matrix(1,lattice_size_x,1,lattice_size_y);
	 d50=matrix(1,lattice_size_x,1,lattice_size_y);
	 rockcover=matrix(1,lattice_size_x,1,lattice_size_y);
	 if (flagfortaucsoilandveg==0) 
	  {for (j=1;j<=lattice_size_y;j++)
	    for (i=1;i<=lattice_size_x;i++)
	     taucsoilandveg[i][j]=taucsoilandvegfixed;}
	  else
       {fp4=fopen("./taucsoilandveg.txt","r");
		for (j=1;j<=lattice_size_y;j++)
	     for (i=1;i<=lattice_size_x;i++)
	      fscanf(fp4,"%f",&taucsoilandveg[i][j]);
	    fclose(fp4);}	
	 if (flagford50==0) 
	  {for (j=1;j<=lattice_size_y;j++)
	    for (i=1;i<=lattice_size_x;i++)
		 d50[i][j]=d50fixed;} 
	  else 
	   {fp4=fopen("./d50.txt","r");
		for (j=1;j<=lattice_size_y;j++)
	     for (i=1;i<=lattice_size_x;i++)
	      fscanf(fp4,"%f",&d50[i][j]);
	    fclose(fp4);}
	 if (flagforrockcover==0) 
	  {for (j=1;j<=lattice_size_y;j++)
	    for (i=1;i<=lattice_size_x;i++)
	     rockcover[i][j]=rockcoverfixed;}
	  else
       {fp4=fopen("./rockcover.txt","r");
		for (j=1;j<=lattice_size_y;j++)
	     for (i=1;i<=lattice_size_x;i++)
	      fscanf(fp4,"%f",&rockcover[i][j]);
	    fclose(fp4);}
	 taucarmor=matrix(1,lattice_size_x,1,lattice_size_y);
	 tauwithoutrain=matrix(1,lattice_size_x,1,lattice_size_y);
	 dischargewithoutrain=matrix(1,lattice_size_x,1,lattice_size_y);
	 taucsoilandveg=matrix(1,lattice_size_x,1,lattice_size_y);
	 rain=matrix(1,lattice_size_x,1,lattice_size_y);
	 if (flagfordynamicmode==0)
	  {for (j=1;j<=lattice_size_y;j++)
        for (i=1;i<=lattice_size_x;i++)
	     rain[i][j]=rainfixed;}
	 for (j=1;j<=lattice_size_y;j++)
      for (i=1;i<=lattice_size_x;i++)
	   if (mask[i][j]==1)
	    {if (flagforequation==0) taucarmor[i][j]=9810*sinofslope[i][j]*pow(1.9*pow(slope[i][j],-1.15)*pow(d50[i][j],2.13)/cosofslopeterm[i][j],0.666667);
	      else taucarmor[i][j]=9810*sinofslope[i][j]*pow(1.3*pow(slopefactor[i][j],-0.86)*pow(d50[i][j],1.68)/cosofslopeterm[i][j],0.666667);     
	     if (taucarmor[i][j]<taucsoilandveg[i][j]) taucarmor[i][j]=taucsoilandveg[i][j];
		 if ((rockcover[i][j]<0.99)&&(rockcover[i][j]>0.3)) taucarmor[i][j]/=exp(-4*(rockcover[i][j]-0.1));
		 dischargewithoutrain[i][j]=b/(1000*3600)*pow(area[i][j],c);
		 tauwithoutrain[i][j]=9810*sinofslope[i][j]*pow(dischargewithoutrain[i][j]/cosofslopeterm[i][j],0.666667);} 
	 free_matrix(taucsoilandveg,1,lattice_size_x,1,lattice_size_y);
	 free_matrix(d50,1,lattice_size_x,1,lattice_size_y);
	 free_matrix(rockcover,1,lattice_size_x,1,lattice_size_y);
	 free_matrix(slopefactor,1,lattice_size_x,1,lattice_size_y);
	 free_matrix(sinofslope,1,lattice_size_x,1,lattice_size_y);
	 free_matrix(cosofslopeterm,1,lattice_size_x,1,lattice_size_y);
	 f=matrix(1,lattice_size_x,1,lattice_size_y);
     f2=matrix(1,lattice_size_x,1,lattice_size_y);	 
	 if (flagfordynamicmode!=0)
	  {fpin=fopen("./dynamicinput.txt","r");
	   fscanf(fpin,"%d",&flagforrainrasters);		 
	   fscanf(fpin,"%f",&rillerodibility);		
	   fscanf(fpin,"%f",&bulkdensity);		 	 
	   fscanf(fpin,"%f",&timescaleofinterest);
       fscanf(fpin,"%f",&durationofdata);
	   fscanf(fpin,"%f",&timestep);
	   fscanf(fpin,"%d",&numberofraingages);
	   fscanf(fpin,"%f",&ulx,&uly);
	   inciseddepth=matrix(1,lattice_size_x,1,lattice_size_y);
	   rainl=matrix(1,lattice_size_x,1,lattice_size_y);
	   for (j=1;j<=lattice_size_y;j++)
        for (i=1;i<=lattice_size_x;i++)
		 inciseddepth[i][j]=0;
	   fp4=fopen("./inciseddepth.txt","w");
	   if (flagforrainrasters==0)
	    {raingagex=vector(1,numberofraingages);
	     raingagey=vector(1,numberofraingages);
		 closestgage=imatrix(1,lattice_size_x,1,lattice_size_y); 
	     for (m=1;m<=numberofraingages;m++) fscanf(fpin,"%f %f",&raingagex[m],&raingagey[m]);
	     for (j=1;j<=lattice_size_y;j++)
          for (i=1;i<=lattice_size_x;i++)
		   {mindist=large;
	        for (m=1;m<=numberofraingages;m++) 
		     {ic=oneoverdeltax*(raingagex[m]-ulx);
		      jc=oneoverdeltax*(uly-raingagey[m]);
		      dist=sqrt((i-ic-1)*(i-ic-1)+(j-jc-1)*(j-jc-1));
		      if (dist<mindist) {mindist=dist;closestgage[i][j]=m;}}}}
	   fscanf(fpin,"%d",&numberofraindata);	 
	   if (flagforrainrasters==0) rainvalues=vector(1,numberofraindata); else fp5=fopen("./rainrasters.txt","r");    
	   for (n=1;n<=numberofraindata;n++)
	    {if (flagforrainrasters==0) for (m=1;m<=numberofraingages;m++) fscanf(fpin,"%f",&rainvalues[m]);
		  else 
		   {for (j=1;j<=lattice_size_y;j++)
             for (i=1;i<=lattice_size_x;i++)
			  fscanf(fp5,"%f",&rainl[i][j]);}
		 for (j=1;j<=lattice_size_y;j++)
          for (i=1;i<=lattice_size_x;i++)
		   {if (flagforrainrasters==0) rainl[i][j]=rainvalues[closestgage[i][j]];
	        if (rainl[i][j]>rain[i][j]) rain[i][j]=rainl[i][j];
		    rillwidth=rillwidthcoefficient*pow(rainl[i][j]*dischargewithoutrain[i][j],rillwidthexponent);
		    if (rillwidth>deltax) rillwidth=deltax;
			f[i][j]=taucarmor[i][j]/(tauwithoutrain[i][j]*pow(rainl[i][j]/rillwidth,0.666667));
			if ((slope[i][j]<tanangleofinternalfriction)&&(f[i][j]<1)) 
		     inciseddepth[i][j]+=rillerodibility*(tauwithoutrain[i][j]*pow(rainl[i][j]/rillwidth,0.666667)-taucarmor[i][j])*timescaleofinterest*60*timestep/(bulkdensity*durationofdata);}}		   
	   for (j=1;j<=lattice_size_y;j++)
        for (i=1;i<=lattice_size_x;i++)
	     if (mask[i][j]==1) fprintf(fp4,"%f\n",inciseddepth[i][j]); else  fprintf(fp4,"0.0\n");
	   fclose(fpin);fclose(fp4);
	   if (flagforrainrasters==1) fclose(fp5);}
	 for (j=1;j<=lattice_size_y;j++)
      for (i=1;i<=lattice_size_x;i++)
	   if (slope[i][j]<tanangleofinternalfriction) 
	    {rillwidth=rillwidthcoefficient*pow(rain[i][j]*dischargewithoutrain[i][j],rillwidthexponent);
		 if (rillwidth>deltax) rillwidth=deltax;
		 f[i][j]=taucarmor[i][j]/(tauwithoutrain[i][j]*pow(rain[i][j]/rillwidth,0.666667)); }
	   else f[i][j]=1;    
	 for (j=1;j<=lattice_size_y;j++)
      for (i=1;i<=lattice_size_x;i++)
	   {if (mask[i][j]==1) 
	     {if ((f[i][j]<2)&&(f[i][j]>-large)&&(f[i][j]<large)) fprintf(fp1,"%f\n",f[i][j]); 
		   else {if (f[i][j]>2) fprintf(fp1,"2.0\n"); else fprintf(fp1,"0.0\n");}}
	    else fprintf(fp1,"0.0\n");
		if (mask[i][j]==1) 
		 {rillwidth=rillwidthcoefficient*pow(rain[i][j]*dischargewithoutrain[i][j],rillwidthexponent);
		  if (rillwidth>deltax) rillwidth=deltax;
		  fprintf(fp3,"%f\n",tauwithoutrain[i][j]*pow(rain[i][j]/rillwidth,0.666667));}
		else  fprintf(fp3,"0.0\n");}
     fprintf(fp2,"P3\n%ld %ld\n255\n",lattice_size_x,lattice_size_y);	 
	 for (m=1;m<=expansion;m++)
	  {for (j=1;j<=lattice_size_y;j++)
        for (i=1;i<=lattice_size_x;i++)
		 f2[i][j]=f[i][j];
	   for (j=1;j<=lattice_size_y;j++)
        for (i=1;i<=lattice_size_x;i++)
	     if ((f2[iup[i]][j]<=1)||(f2[idown[i]][j]<=1)||(f2[i][jup[j]]<=1)||(f2[i][jdown[j]]<=1)) f[i][j]=0.99;}
	 for (m=1;m<=expansion;m++)
	  {for (j=1;j<=lattice_size_y;j++)
        for (i=1;i<=lattice_size_x;i++)
		 f2[i][j]=f[i][j];
	   for (j=1;j<=lattice_size_y;j++)
        for (i=1;i<=lattice_size_x;i++)
	     if (((f2[iup[i]][j]<=yellowthreshold)&&(f2[i][j]>1))||((f2[idown[i]][j]<=yellowthreshold)&&(f2[idown[i]][j]>1))||((f2[i][jup[j]]<=yellowthreshold)&&(f2[i][jup[j]]>1))||((f2[i][jdown[j]]<=yellowthreshold)&&(f2[i][jdown[j]]>1))) f[i][j]=yellowthreshold-0.01;}
	 for (j=1;j<=lattice_size_y;j++)
      for (i=1;i<=lattice_size_x;i++)
	   if (mask[i][j]==0) fprintf(fp2,"0 0 0\n"); else {if (f[i][j]<1) fprintf(fp2,"255 0 0\n"); else if (f[i][j]<yellowthreshold) fprintf(fp2,"255 255 0\n"); else fprintf(fp2,"255 255 255\n");}
     fclose(fp0);fclose(fp1);fclose(fp2);fclose(fp3);
}  