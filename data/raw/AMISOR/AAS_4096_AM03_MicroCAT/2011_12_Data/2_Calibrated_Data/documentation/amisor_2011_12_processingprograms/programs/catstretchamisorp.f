c   this program takes the file output from catfixamisor.f
c   and corrects the times by stretching them (as all microcats
c   were a couple of minutes fast at the final clock check).
c
c   the input correction file "stretch.in" has filename,time in days between logging start
c   and clock check,time in minutes that instrument is fast
c
c
c  this version for borehole microcats with pressure sensor
c
c
c    M.R. June 2002
c
c
       program catstretchamisorp

       real t,xnull
       real c,s,p
       real*16 dectime,dectimeold,digint,ddi
       real*16 dectimenew
       real*16 xlen,diff,corr,startdiff
       real*16 ms,ff,startadd,clockstart
       integer mon,ixnull
       integer day,year
       integer hr,min,sec,itype
       character*79 batfile,cmfile,outfile

       save

       write(*,10)
10     format(/'enter type of instrument :'
     $        /'       1=SBE37-SM   '
     $        /'       2=SBE39-SM   '
     $        /'   enter 1 or 2      :   ',$)
       read(*,*) itype
       write(*,15)
15     format(/'enter list with microcat files and corrections : ',$)
       read(*,20) batfile
20     format(a)
       open(unit=1,file=batfile,status='old')
       write(*,23)
23     format(/'input record interval in seconds : ',$)
       read(*,*) digint
       ddi=((digint/60.)/60.)/24.
       xnull=-999.
       ixnull=-999
       write(*,24)
24     format(/'enter decimal time of start clock check : ',$)
       read(*,*) clockstart


       do 9000, iii=1,300

        read(1,30,end=8500) cmfile,xlen,diff,startdiff
        diff=((diff/60.)/60.)/24.
        startdiff=((startdiff/60.)/60.)/24.
        outfile=cmfile(1:6)//'.dat'
        open(unit=3,file=cmfile,status='old')
        open(unit=4,file=outfile,status='unknown')
        write(*,20) cmfile

30      format(a10,f9.4,2f7.1)
201   format(f10.5,3x,2(x,f9.4),x,f9.3,x,f9.4,x,2(x,i2.2),
     $        x,i4.4,3(x,i2.2))
202     format(f10.5,3x,x,f9.4,2(x,i2.2),x,i4.4,3(x,i2.2))
c  read the first line of data
c    (need to do this separately in order to get an initial dectimeold
c      value)
c
        if(itype.eq.1) then
         read(3,201) dectime,t,c,p,s,day,mon,year,hr,
     $              min,sec
        endif
        if(itype.eq.2) then
         read(3,202) dectime,t,day,mon,year,hr,
     $              min,sec
        endif
c        ms=(float(sec/60.)+float(min))/5.
c        ff=float(int(ms))
c        ms=(((ms-ff)*5.)/60.)/24.
c        startadd=startdiff-ms
c        dectime=dectime+startadd
        corr=((dectime-clockstart)/xlen)*diff
        dectimenew=dectime-corr
        call unpacktime(hr,min,sec,dectimenew)
        call unpackdate(day,mon,year,dectimenew)
        if(itype.eq.1) then
         write(4,201) dectimenew,t,c,p,s,day,mon,year,
     $   hr,min,sec
        endif
        if(itype.eq.2) then
         write(4,202) dectimenew,t,day,mon,year,
     $   hr,min,sec
        endif
        dectimeold=dectimenew
c         
c
c  now read the data
        do 8000, kk=1,999999999

        if(itype.eq.1) then
         read(3,201,end=8900) dectime,t,c,p,s,day,mon,year,hr,
     $   min,sec
        endif
        if(itype.eq.2) then
         read(3,202,end=8900) dectime,t,day,mon,year,hr,
     $   min,sec
        endif
c
c  these next few lines account for fact that first record wasn't 
c  at exactly 12:00:00 on 14/02/2001
c
c        ms=(float(sec/60.)+float(min))/5.
c        ff=float(int(ms))
c        ms=(((ms-ff)*5.)/60.)/24.
c        startadd=startdiff-ms
c        dectime=dectime+startadd
c
c        dectime=dectimeold+ddi
        corr=((dectime-clockstart)/xlen)*diff
        dectimenew=dectime-corr
        call unpacktime(hr,min,sec,dectimenew)
        call unpackdate(day,mon,year,dectimenew)
        if(itype.eq.1) then
         write(4,201) dectimenew,t,c,p,s,day,mon,year,
     $   hr,min,sec
        endif
        if(itype.eq.2) then
         write(4,202) dectimenew,t,day,mon,year,
     $   hr,min,sec
        endif
        dectimeold=dectime

8000    continue

8900   close(3)
       close(4)

9000   continue

8500   stop
       end
c
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

c correction for data in 2002
         if(decday.gt.365.)decday=decday-365.
c correction for data in 2003
         if(decday.gt.365.)decday=decday-365.
c correction for data in 2004
         if(decday.gt.365.)decday=decday-365.
c correction for data in 2005
         if(decday.gt.366.)decday=decday-366.
c correction for data in 2006
         if(decday.gt.365.)decday=decday-365.
c correction for data in 2007
         if(decday.gt.365.)decday=decday-365.
c correction for data in 2008
         if(decday.gt.365.)decday=decday-365.
c correction for data in 2009
         if(decday.gt.366.)decday=decday-366.
c correction for data in 2010
         if(decday.gt.366.)decday=decday-365.
c correction for data in 2011
         if(decday.gt.366.)decday=decday-365.
c correction for data in 2012
         if(decday.gt.366.)decday=decday-365.
c correction for data in 2013
         if(decday.gt.366.)decday=decday-366.
c correction for data in 2014
         if(decday.gt.366.)decday=decday-365.
c correction for data in 2015
         if(decday.gt.366.)decday=decday-365.
c correction for data in 2016
         if(decday.gt.366.)decday=decday-365.
c correction for data in 2017
         if(decday.gt.366.)decday=decday-366.
c correction for data in 2018
         if(decday.gt.366.)decday=decday-365.
c correction for data in 2019
         if(decday.gt.366.)decday=decday-365.
c correction for data in 2020
         if(decday.gt.366.)decday=decday-365.

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
