c   this program reads a Microcat file, fixes the 
c   format and fills data gaps; also fixes up the conductivity so
c that it's calculated using the correct deployment pressure, using the
c Seabird formula; then also calculates salinity, where
c   pressure for each instrument is from the mooring diagrams
c   and is assumed constant for each instrument.
c
c    M.R. May 2000
c
c  N.B. conductivity multiplied by 10 in subroutine dataread
c
c   this version is for microcats which have a pressure sensor
c      M.R. Sep. 2001
c
       program catfixp

       real t,c,told,cold,pold,xnull,s,sold,p
       real*16 dectime,dectimeold,frac,digint,ddi,decday
       real*16 dectimefill,startdec,enddec,yyy
       real*16 diff,dectimeround
       integer itype,mon,monold
       integer day,year,dayold,yearold,vvv,yearstart
       integer hr,min,sec,hrold,minold,secold
       integer daynew,monnew,yearnew,hrnew,minnew,secnew
       character*79 infile,catfile,newfile
       character bla*80,bb*4
       character date*12,time*9
       character dateold*12,timeold*9

       save

       write(*,4)
 4     format(/'WARNING: times/dates for gapfill and endpad '
     $        /' do not take leap years into account!!!!'
     $        /'          ') 
       write(*,10)
10     format(/'enter type of instrument :'
     $        /'       1=SBE37-SM   '
     $        /'       2=SBE39-SM   '
     $        /'   enter 1 or 2      :   ',$)
       read(*,*) itype
       write(*,15)
15     format(/'enter file with list of files : ',$)
       read(*,20) infile
20     format(a)
       open(unit=1,file=infile,status='old')
       write(*,23)
23     format(/'input record interval in seconds : ',$)
       read(*,*) digint
       ddi=((digint/60.)/60.)/24.
       xnull=-999.
       write(*,24)
24     format(/'enter start decimal time to pad files from : ',$)
       read(*,*) startdec
       write(*,26)
26     format(/'enter end decimal time to pad files to : ',$)
       read(*,*) enddec
       if(enddec.le.startdec) then
        enddec=enddec+365.
       endif
       write(*,28)
28     format(/'enter no. of days to add to all time '
     $        /'    (time base starts at start of '
     $        /'    start of 2001)  : ',$)
       read(*,*) yyy

       do 9000, k=1,500

        read(1,20,end=9500) catfile
        write(*,20) catfile
        open(unit=2,file=catfile,status='old')
        newfile=catfile(1:6)//'.fix'
        open(unit=3,file=newfile,status='unknown')

c
c  find out how many header lines
        do 40, j=1,1000
         read(2,20) bla
         if(itype.eq.1)bb=bla(39:42)
         if(itype.eq.2)bb=bla(18:21)
         if(bb.eq.'1998'.or.bb.eq.'1999'.or.bb.eq.'2000'.or.bb.
     $     eq.'2001'.or.bb.eq.'2002'.or.bb.eq.'2003'.or.bb.
     $     eq.'2004'.or.bb.eq.'2005'.or.bb.eq.'2006'.or.bb.
     $     eq.'2007'.or.bb.eq.'2008'.or.bb.eq.'2009'.or.bb.
     $     eq.'2010'.or.bb.eq.'2011'.or.bb.eq.'2012')then
          goto 50
         endif
40      continue

c  read header lines
50      rewind(2)
        do 55, jj=1,j-1
         read(2,20) bla
55      continue

200     format(f10.5,3x,2(x,f9.4),x,f9.3,x,f9.4,x,2(x,i2.2),x,i4,
     $         3(x,i2.2))
201     format(f10.5,3x,x,f9.4,2(x,i2.2),x,i4,3(x,i2.2))
c  read the first line of data
        call dataread(told,cold,pold,dateold,timeold,itype,ilast)
        if(itype.eq.1) then
         if(cold.eq.-999.or.told.eq.-999.or.pold.eq.-999.) then
          sold=-999.
         else
          sold=sal(cold,told*1.00024,pold,0)
         endif
        endif
        read(dateold(2:3),*) dayold
        read(dateold(9:12),*) yearold
        yearstart=yearold
        call monthname(dateold(5:7),monold)
        read(timeold(2:3),*) hrold
        read(timeold(5:6),*) minold
        read(timeold(8:9),*) secold

        call decimalt(hrold,minold,secold,frac,dayold,monold,
     $     yearold,decday)
        dectimeold=decday+frac
c
c   pad start of file from start dectime specified
c
        nfill=int((dectimeold-startdec)/ddi+0.5)
        dectimefill=startdec
        do 60, kk=1,nfill
           call unpacktime(hr,min,sec,dectimefill)
           call unpackdate(day,mon,yearold,dectimefill)
           if(itype.eq.1) then
            write(3,200) dectimefill+yyy,xnull,xnull,xnull,xnull,day,
     $        mon,yearold,hr,min,sec
           endif
           if(itype.eq.2) then
            write(3,201) dectimefill+yyy,xnull,day,mon,yearold,
     $        hr,min,sec
           endif
           dectimefill=dectimefill+ddi
60      continue
         
        if(itype.eq.1) then
         write(3,200) dectimeold+yyy,told,cold,pold,sold,dayold,
     $     monold,yearold,hrold,minold,secold
        endif
        if(itype.eq.2) then
         write(3,201) dectimeold+yyy,told,dayold,monold,yearold,
     $     hrold,minold,secold
        endif
c
c  now read the data
        do 8000, kk=1,999999999

         call dataread(t,c,p,date,time,itype,ilast)
         if(ilast.eq.1)goto 8500
         if(itype.eq.1) then
          if(c.eq.-999.or.t.eq.-999.or.p.eq.-999.) then
           s=-999.
          else
           s=sal(c,t*1.00024,p,0)
          endif
         endif
         read(date(2:3),*) day
         read(date(9:12),*) year
         call monthname(date(5:7),mon)
         read(time(2:3),*) hr
         read(time(5:6),*) min
         read(time(8:9),*) sec

         call decimalt(hr,min,sec,frac,day,mon,year,decday)
         dectime=decday+frac
c
c        assign following so times are correct at the end of each data gap
c
         hrnew=hr
         minnew=min
         secnew=sec
         daynew=day
         monnew=mon
         yearnew=year
c
c           first take care of the case where we cross into a new year
c
c         if(abs(dectime-dectimeold).ge.360.) then
c           if(itype.eq.1) then
c            write(3,200) dectime+yyy,t,c,p,s,daynew,monnew,yearnew,
c     $        hrnew,minnew,secnew
c           endif
c           if(itype.eq.2) then
c            write(3,201) dectime+yyy,t,daynew,monnew,yearnew,
c     $        hrnew,minnew,secnew
c           endif
c           dectimeold=dectime
c
c           goto 8000
c         endif

        vvv=yearnew-yearstart

        if(yearstart.eq.2004.or.yearstart.eq.2008.) then

         if(vvv.eq.1.) then
          dectime=dectime+366. 
         endif
         if(vvv.eq.2.) then
          dectime=dectime+366.+365. 
         endif

        else

         dectime=dectime+vvv*365. 

        endif
c
c       now test for data gaps
c
         do 90, j=1,200000
          if((dectime-dectimeold).lt.(ddi*0.2)) then
           goto 8000
          endif
          if((dectime-dectimeold).gt.(ddi+0.5*ddi)) then
           dectimefill=dectimeold+ddi
c
c now to take care of any 240000 time problem
           dectimeround=float(int(dectimefill+.05))
           diff=abs(dectimefill-dectimeround)
           if(diff.lt.0.00001.and.diff.ne.0.) then
            dectimefill=dectimeround
           endif
c
c
           call unpacktime(hr,min,sec,dectimefill)
           call unpackdate(day,mon,year,dectimefill-vvv*365.)
           if(itype.eq.1) then
            write(3,200) dectimefill+yyy,xnull,xnull,xnull,xnull,
     $        day,mon,year,hr,min,sec
           endif
           if(itype.eq.2) then
            write(3,201) dectimefill+yyy,xnull,day,mon,year,hr,
     $        min,sec
           endif
           dectimeold=dectimefill
          else
           if(itype.eq.1) then
            write(3,200) dectime+yyy,t,c,p,s,daynew,monnew,yearnew,
     $        hrnew,minnew,secnew
           endif
           if(itype.eq.2) then
            write(3,201) dectime+yyy,t,daynew,monnew,yearnew,
     $        hrnew,minnew,secnew
           endif
           dectimeold=dectime
c
           goto 8000
          endif
 90      continue

8000    continue
c
c     now pad out end of file
c
8500    do 8600, j=1,999999999
        dectimefill=dectimeold+ddi
c        write(*,*) dectimeold,dectimefill,enddec
        if(dectimefill.ge.enddec) then
         goto 9000
        else
         call unpacktime(hr,min,sec,dectimefill)
         if(enddec.le.startdec) then
          call unpackdate(day,mon,year,dectimefill-365.)
         elseif(dectimefill.gt.365.and.dectimefill.lt.730.) then
          call unpackdate(day,mon,year,dectimefill-365.)
         elseif(dectimefill.gt.730.) then
          call unpackdate(day,mon,year,dectimefill-2.*365.)
         else
          call unpackdate(day,mon,year,dectimefill)
         endif
         if(itype.eq.1) then
          write(3,200) dectimefill+yyy,xnull,xnull,xnull,xnull,
     $      day,mon,year,hr,min,sec
         endif
         if(itype.eq.2) then
          write(3,201) dectimefill+yyy,xnull,day,mon,year,hr,
     $      min,sec
         endif
         dectimeold=dectimefill
        endif
8600    continue

9000   continue

9500   stop
       end
c
c
c
c
c
c
c
       subroutine dataread(t,c,p,date,time,itype,ilast)

c   reads a line of data from the file

       real t,c,p
       integer itype
       character crec*900,rec(10)*15
       character date*12,time*9

       save

20     format(a)

       do ii=1,10
        do jj=1,15
          rec(ii)(jj:jj)=''
        enddo
       enddo
 
       read(2,60,iostat=ios,end=8000)noc,crec
60     format(q,a)
       lasti=0
       j=0
       i=index(crec(1:noc),char(o"054"))
       read(crec(1:i-1),*,iostat=ios)istat
       if(i.ne.0) then     ! test for data in line
        do while (i.gt.0)
         j=j+1
         if(lasti+1.gt.lasti+i-1)then
          rec(j)=' '
         else
          rec(j)=crec(lasti+1:lasti+i-1)
         endif
         lasti=lasti+i
         i=index(crec(lasti+1:noc),char(o"054"))
        enddo
        j=j+1
        rec(j)=crec(lasti+1:noc)
       else
c        type *,'This record has no data'
        goto 7000
       endif
c
       if(itype.eq.1) then

        if(rec(1).ne.' ')then
         read(rec(1),*)t
        else
         t=-999.
        endif
        if(t.eq.-9.) then
         t=-999.
        endif

        if(rec(2).ne.' ')then
         read(rec(2),*)c
         c=c*10.
        else
         c=-999.
        endif
        if(c.eq.-90.) then
         c=-999.
        endif

        if(rec(3).ne.' ')then
         read(rec(3),*)p
        else
         p=-999.
        endif
        if(p.eq.-9.) then
         p=-999.
        endif

        if(rec(4).ne.' ')then
         read(rec(4),20)date
        else
         date='            '
        endif
        if(rec(5).ne.' ')then
         read(rec(5),20)time
        else
         time='         '
        endif
       endif

       if(itype.eq.2) then
        if(rec(1).ne.' ')then
         read(rec(1),*)t
        else
         t=-999.
        endif
        if(t.eq.-9.) then
         t=-999.
        endif

        c=-999.
        if(rec(2).ne.' ')then
         read(rec(2),20)date
        else
         date='            '
        endif
        if(rec(3).ne.' ')then
         read(rec(3),20)time
        else
         time='         '
        endif
       endif

       ilast=0
7000   return

8000   ilast=1
       return

       end
c
c
c
         subroutine monthname(month,mon)
c
c        converts month name to month number
c
         character month*3
         integer mon
         save
c
         if(month.eq.'Jan') then
          mon=1
         endif
         if(month.eq.'Feb') then
          mon=2
         endif
         if(month.eq.'Mar') then
          mon=3
         endif
         if(month.eq.'Apr') then
          mon=4
         endif
         if(month.eq.'May') then
          mon=5
         endif
         if(month.eq.'Jun') then
          mon=6
         endif
         if(month.eq.'Jul') then
          mon=7
         endif
         if(month.eq.'Aug') then
          mon=8
         endif
         if(month.eq.'Sep') then
          mon=9
         endif
         if(month.eq.'Oct') then
          mon=10
         endif
         if(month.eq.'Nov') then
          mon=11
         endif
         if(month.eq.'Dec') then
          mon=12
         endif
c
         return
         end
 
c
c
      subroutine decimalt(hr,min,sec,frac,day,mon,yr,decday)
c
c     this subroutine calculates decimal fraction of day, given hour,min and sec.
c     decimal day value (in whole days) is also passed through
c     by calling subroutine decimald
c
      real*16 frac,decday
      integer day,mon,yr,hr,min,sec
      save
      frac=((float(sec)/60.+float(min))/60.+float(hr))/24.
      call decimald(day,mon,yr,decday)
      if(sec.eq.60) then
       sec=0
       min=min+1
      endif
      if(min.eq.60) then
       min=0
       hr=hr+1
      endif
      return
      end
c
c
      subroutine decimald(day,mon,yr,decday)
c
c     this subroutine calculates decimal day, given day, month and year
c     Remember that Jan 1st is day 0
c
      real*16 decday
      integer day,mon,yr,mdays
         integer monthl(12)
         data monthl/31,28,31,30,31,30,31,31,30,31,30,31/
         save
c
         mdays=0
         call leapyr(leap,yr,monthl)
         if (mon.eq.1) then
         decday=(day-1)
         else
         do 1060 k=1,(mon-1)
          mdays=mdays+monthl(k)
1060     continue
         decday=(mdays+day)-1
         end if
         return
         end
c
c
         subroutine leapyr(leap,yr,monthl)
c
c        tests to see if year is a leap year
c
         integer monthl(12),iyr,yr,leap
         save
c
         if(yr.gt.99) then
           iyr=yr-1900
         else
           iyr=yr
         end if
         if ((iyr/4)*4.eq.iyr) then
         monthl(2)=29
         leap=1
         else
         monthl(2)=28
         leap=0
         end if
         return
         end
c
c
      subroutine unpacktime(hr,min,sec,dectime)
c
c     this subroutine unpacks decimal time into hour, min, and sec.
c
      real*8 xx
      real*16 dectime,frac
      integer hr,min,sec
      save
      frac=dectime-float(int(dectime))
      hr=int(24.*frac)
      xx=(24.*frac-float(hr))*60.
      min=int(xx)
      sec=int((xx-float(min))*60.+0.5)
      if(sec.eq.60) then
       sec=0
       min=min+1
      endif
      if(min.eq.60) then
       min=0
       hr=hr+1
      endif
      return
      end
c
c
c
         subroutine unpackdate(day,mon,yr,dectime)
c
c        this subroutine unpacks decimal day into day, month (and year)
c
         real*16 dectime,decday
         integer day,mon,yr
         integer monthl(12),jd,mdays
         data monthl/31,28,31,30,31,30,31,31,30,31,30,31/
         save
c
         decday=float(int(dectime))
         call leapyr(leap,yr,monthl)
C
         i=1
         jd=decday+1
         if (jd.gt.monthl(i)) then
          mdays=monthl(i)
         else
          day=jd
          mon=i
          yr=yr
          goto 300
         end if
C
         do 250 i=2,12
         mdays=mdays+monthl(i)
         if (jd.gt.mdays) goto 250
         day=jd-(mdays-monthl(i))
         mon=i
         yr=yr
         goto 300
250      continue
300      return
         end
c
c
c
c
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
