c   this program reads a Microcat file *.god file
c  and then removes all the data dump resets - did it
c  for 2007/08 borehole data as Mark Milne did the
c  data dumps in 200 point lots, so there's a set of
c  dump info lines every 200 data pts - want to get rid
c  of these before doing anything else.
c
c    M.R. June 2008
c
c   this version is for microcats which have a pressure sensor
c
       program catgodfixp

       real t,c,told,cold,pold,xnull,s,sold,p
       real*16 dectime,dectimeold,frac,digint,ddi,decday
       real*16 dectimefill,startdec,enddec,yyy
       integer itype,mon,monold
       integer day,year,dayold,yearold,vvv,yearstart
       integer hr,min,sec,hrold,minold,secold
       integer daynew,monnew,yearnew,hrnew,minnew,secnew
       character*79 infile,catfile,newfile
       character bla*80,bla1*52,bb*4
       character date*12,time*9
       character dateold*12,timeold*9

       save

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

       do 9000, k=1,500

        read(1,20,end=9500) catfile
        write(*,20) catfile
        open(unit=2,file=catfile,status='old')
        newfile=catfile(1:6)//'.godfix'
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
         write(3,20) bla
55      continue

200     format(f10.5,3x,2(x,f9.4),x,f9.3,x,f9.4,x,2(x,i2.2),x,i4,
     $         3(x,i2.2))
201     format(f10.5,3x,x,f9.4,2(x,i2.2),x,i4,3(x,i2.2))


        do 300, kk=1,999999999
         read(2,20,end=9000) bla1
         if(bla1(41:41).ne.' '.and.bla1(42:42).ne.' ') then
          write(3,20) bla1
         endif
300     continue

9000    continue

9500    stop
        end






