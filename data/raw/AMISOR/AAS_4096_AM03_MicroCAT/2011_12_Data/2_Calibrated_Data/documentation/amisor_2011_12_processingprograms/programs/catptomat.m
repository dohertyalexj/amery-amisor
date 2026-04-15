file=input('enter name of file to load : ','s');
eval(['load -ascii ' file]);
[m,n]=size(file);
ff=file(1:n-4);
gg=file(1:n-4);
eval(['a=find(',ff,'==-999.);']);
eval([ff,'(a)=NaN.*',ff,'(a);']);
eval([gg,'_dectime=',ff,'(:,1);']);
eval(['t=',ff,'(:,2);']);
eval(['c=',ff,'(:,3);']);
eval(['p=',ff,'(:,4);']);
eval(['s=',ff,'(:,5);']);

eval(['day=',ff,'(:,6);']);
eval(['month=',ff,'(:,7);']);
eval(['year=',ff,'(:,8);']);
date=1000000.*day+10000*month+year;
eval(['hr=',ff,'(:,9);']);
eval(['min=',ff,'(:,10);']);
eval(['sec=',ff,'(:,11);']);
time=10000.*hr+100.*min+sec;

%a=find(c<=20);
%c(a)=NaN.*c(a);
%a=find(s<=20);
%s(a)=NaN.*s(a);
%a=find(t>=5);
%t(a)=NaN.*t(a);
eval([gg,'_temp=t;']);
eval([gg,'_cond=c;']);
eval([gg,'_press=p;']);
eval([gg,'_sal=s;']);
eval([gg,'_date=date;']);
eval([gg,'_time=time;']);

eval(['save ',gg,' ',gg,'_cond ',gg,'_sal ',gg,'_temp ', ...
gg,'_press ',gg,'_dectime ',gg,'_date ',gg,'_time']);

eval(['clear ',gg])
eval(['clear ',ff])
clear t c s p
clear day month year hr min sec date time
clear n m a ff file gg

