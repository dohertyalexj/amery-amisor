c corrects amisor borehole AM05 and AM06 data for the
c shallowest microcat: detrends the drifting pressure,
c then recalculates cond and sal from this new pressure
c note: needs as input the pressure slope,offset correction 
c  factors from running of correctp.m
c
c   M.R. Nov 2012
c

        program correctam05am06_2

        character*79 infile,newfile
        character date*19,bla1*42,bla2*51
        character bla3*74
        real*16 dect
        real t,c,p,s
        real slope,offset,p1,p2,dect1,dect2
        real pcor1,pcor2,pmax,ctcor,cpcor,padd
        integer i1,i2,i
        save

        write(*,10)
10      format(/'enter name of input file : ',$)
        read(*,15) infile
15      format(a)
        write(*,20)
20      format(/'enter pressure slope correction: ',$)
        read(*,*) slope
        write(*,25)
25      format(/'enter pressure offset correction: ',$)
        read(*,*) offset
        write(*,30)
30      format(/'enter 1st reference pressure data point no. : ',$)
        read(*,*) i1
        write(*,35)
35      format(/'enter 2nd reference pressure data point no. : ',$)
        read(*,*) i2
        write(*,37)
37      format(/'enter padd value : ',$)
        read(*,*) padd
        ctcor=3.25e-06
        cpcor=-9.57e-08
50      format(f10.5,4x,f9.4,x,f9.4,2x,f8.3,x,f9.4,2x,a19)

        open(unit=1,file=infile,status='old')
        newfile=infile(1:10)//'new'
        open(unit=2,file=newfile,status='unknown')

c        first, read through file to get reference press. and dectime values
        do 95, i=1,4
         read(1,15)
95      continue
        do 100, i=1,999999999
         read(1,50,end=200) dect,t,c,p,s,date
         if(i.eq.i1) then
          p1=p
          dect1=dect
          pcor1=slope*dect1+offset
         endif
         if(i.eq.i2) then
          p2=p
          dect2=dect
          pcor2=slope*dect2+offset
         endif
100     continue
200     rewind(1)
        pmax=-(pcor2-pcor1)

        read(1,15) bla1
        write(2,15) bla1
        read(1,15) bla2
        write(2,15) bla2
        read(1,15) bla3
        write(2,15) bla3
        read(1,15) bla3
        write(2,15) bla3

        do 300, i=1,999999999
         read(1,50,end=400) dect,t,c,p,s,date

         if(p.eq.-999.) then
          pnew=p
         else
          ptrend=(float(i)-float(i1))/(float(i2)-float(i1))
          pnew=p+pmax*ptrend
          pnew=pnew+padd
         endif
         if(t.eq.-999.or.c.eq.-999.) then
          cnew=c
          snew=s
         else
          del=c*(1+ctcor*t+cpcor*p)
          cnew=del/(1+ctcor*t+cpcor*pnew)
          snew=sal(cnew,t*1.00024,pnew,0)
         endif
          

         write(2,50) dect,t,cnew,pnew,snew,date
300     continue

400     stop
        end





C
      FUNCTION SAL(C,T,P,ifact)
C
C      C35150 IS THE CONDUCTIVITY OF STANDARD SEAWATER AT 35 PRACTICAL
C      SALINITY UNITS, 15 DEGREES, AND ATMOSPHERIC PRESSURE
C
c     declarations (added 20/3/91 PO)
      real   SAL, SAL78, G, C, T, P, C35150
c     end of new declarations

      DATA C35150 / 42.914 /
C
      IF(ABS(C).LT..01)GOTO 900
C
C      ALLOW FOR EFFECTS OF TEMPERATURE AND PRESSURE ON THE
C      CONDUCTIVITY CELL
C
      if(ifact.eq.1) then
        G=(C*(1.-6.5E-06*(T-2.8)+1.5E-8*(P-3000.)))/C35150

      else
        G=C/C35150
      endif

C
      SAL=SAL78(G,T,P,0)
      RETURN
C
C      ERROR - CONDUCTIVITY EFFECTIVELY ZERO
C     
900   SAL=-1.
      RETURN
      END
C
C===============================================================================
C
C      START OF UNESCO ROUTINES
C
C===============================================================================
C  SEPT. 28 1983                                                                
C ADD TF(S,P) FREEZING PT.                                                      
C WHOI CTD GROUP DISK FILE SPEC=BLUE::CTDA:<CTDEV.PRSW>PHYPROPSW.FOR            
C                                                                               
C  TITLE: ALGORITHMS FOR OCEANOGRAPHIC COMPUTATIONS                             
C N FOFONOFF & R MILLARD                                                        
C                                                                               
C SAL78 FCN ********** MAR 28 1983 *******                                      
      REAL FUNCTION SAL78(CND,T,P,M)                                            
C ********************************************************************          
C     THE CONDUCTIVITY RATIO (CND) = 1.0000000 FOR SALINITY = 35 PSS-78         
C     TEMPERATURE = 15.0 DEG. CELSIUS , AND ATMOSPHERIC PRESSURE.               
C********************************************************************           
c     declaration added 20/3/91 PO
c     only to comply with standard use of -u f77 option
      implicit real (A-H)
      implicit real (O-Z)
      implicit integer (I-N)
c     end of declarations
C                                                                               
C FUNCTION TO CONVERT CONDUCTIVITY RATIO TO SALINITY (M = 0)                    
C SALINITY TO CONDUCTIVITY RATIO (M = 1,CND BECOMES INPUT SALINITY)             
C*****************************************************************              
C   REFERENCES:   ALSO LOCATED IN UNESCO REPORT # 37 1981                       
C  PRACTICAL SALINITY SCALE 1978: E.L. LEWIS IEEE OCEAN ENG. JAN. 1980          
C *******************************************************************           
C UNITS:                                                                        
C       PRESSURE        P        DECIBARS                                       
C       TEMPERATURE     T        DEG CELSIUS (IPTS-68)                          
C       CONDUCTIVITY    CND      RATIO     (M=0)                                
C       SALINITY        SAL78    (PSS-78)  (M=0)                                
C  CHECKVALUES:                                                                 
C      SAL78=1.888091 :CND= 40.0000,T=40 DEG C,P= 10000 DECIBARS:   M= 1        
C      SAL78=40.00000 :CND=1.888091,T=40 DEG C,P=10000 DECIBARS:    M=0         
C*******************************************************************            
C SAL78 RATIO: RETURNS ZERO FOR CONDUCTIVITY RATIO:  < 0.0005                   
C SAL78: RETURNS ZERO FOR SALINITY:  < 0.02                                     
C ****************************************************************              
C INTERNAL FUNCTIONS                                                            
C ****************************************************************              
C  PRACTICAL SALINITY SCALE 1978 DEFINITION WITH TEMPERATURE CORRECTION         
C  XT=T-15.0 : XR=SQRT(RT)                                                      
      SAL(XR,XT) =((((2.7081*XR-7.0261)*XR+14.0941)*XR+25.3851)*XR              
     X-0.1692)*  XR+0.0080                                                      
     X  +(XT/(1.0+0.0162*XT))*(((((-0.0144*XR+                                  
     X   0.0636)*XR-0.0375)*XR-0.0066)*XR-0.0056)*XR+0.0005)                    
C  DSAL(XR,XT)  FUNCTION FOR DERIVATIVE OF SAL(XR,XT) WITH XR.                  
      DSAL(XR,XT) =((((13.5405*XR-28.1044)*XR+42.2823)*XR+50.7702)*XR           
     X   -0.1692)+(XT/(1.0+0.0162*XT))*((((-0.0720*XR+0.2544)*XR                
     X   -0.1125)*XR-0.0132)*XR-0.0056)                                         
C  FUNCTION RT35 :  C(35,T,0)/C(35,15,0) VARIATION WITH TEMPERATURE             
C  WITH TEMPERATURE.                                                            
      RT35(XT) = (((1.0031E-9*XT-6.9698E-7)*XT+1.104259E-4)*XT                  
     X   + 2.00564E-2)*XT + 0.6766097                                           
C POLYNOMIALS OF RP: C(S,T,P)/C(S,T,0) VARIATION WITH PRESSURE                  
C  C(XP) POLYNOMIAL CORRESPONDS TO A1-A3 CONSTANTS: LEWIS 1980                  
      C(XP) = ((3.989E-15*XP-6.370E-10)*XP+2.070E-5)*XP                         
      B(XT) = (4.464E-4*XT+3.426E-2)*XT + 1.0                                   
C  A(XT) POLYNOMIAL CORRESPONDS TO B3 AND B4 CONSTANTS: LEWIS 1980              
      A(XT) = -3.107E-3*XT + 0.4215                                             
C*******************************************************************            
C ZERO SALINITY/CONDUCTIVITY TRAP                                               
      SAL78=0.0                                                                 
      IF((M.EQ.0).AND.(CND.LE.5E-4)) RETURN                                     
      IF((M.EQ.1).AND.(CND.LE.0.02)) RETURN                                     
C ***********************************************                               
      DT = T - 15.0                                                             
C SELECT BRANCH FOR SALINITY (M=0) OR CONDUCTIVITY (M=1)                        
      IF(M.EQ.1)  GO TO 10                                                      
C ************************************************                              
C CONVERT CONDUCTIVITY TO SALINITY                                              
      R = CND                                                                   
      RT = R/(RT35(T)*(1.0 + C(P)/(B(T) + A(T)*R)))                             
      RT = SQRT(ABS(RT))                                                        
      SAL78 = SAL(RT,DT)                                                        
      RETURN                                                                    
C *********  END OF CONDUCTIVITY TO SALINITY SECTION ***********                
C *******************************************************                       
C INVERT SALINITY TO CONDUCTIVITY BY THE                                        
C  NEWTON-RAPHSON ITERATIVE METHOD.                                             
C ******************************************************                        
C FIRST APPROXIMATION                                                           
   10 RT = SQRT(CND/35.0)                                                       
      SI = SAL(RT,DT)                                                           
      N = 0                                                                     
C                                                                               
C  ITERATION LOOP BEGINS HERE WITH A MAXIMUM OF 10 CYCLES                       
C                                                                               
   15 RT = RT + (CND - SI)/DSAL(RT,DT)                                          
      SI = SAL(RT,DT)                                                           
      N = N + 1                                                                 
      DELS = ABS(SI - CND)                                                      
      IF((DELS.GT.1.0E-4).AND.(N.LT.10))GO TO 15                                
C                                                                               
C ****************************END OF ITERATION LOOP ********                    
C                                                                               
C COMPUTE CONDUCTIVITY RATIO                                                    
      RTT = RT35(T)*RT*RT                                                       
      AT = A(T)                                                                 
      BT = B(T)                                                                 
      CP = C(P)                                                                 
      CP = RTT*(CP + BT)                                                        
      BT = BT - RTT*AT                                                          
C                                                                               
C SOLVE QUADRATIC EQUATION FOR R: R=RT35*RT*(1+C/AR+B)                          
C                                                                               
      R = SQRT(ABS(BT*BT + 4.0*AT*CP)) - BT                                     
C CONDUCTIVITY RETURN                                                           
      SAL78 = 0.5*R/AT                                                          
      RETURN                                                                    
      END                                                                       
C
C
