clf
set(1,'Papertype','a4letter')
f=input('enter name of file to plot : ','s');
orient tall
subplot(411)
eval(['p=',f,'_press;']);
eval(['[m,n]=size(p);']);
eval(['plot(',f,'_dectime,',f,'_temp)']);
ylabel('temperature (^oC)')
pp=nanmean(p);
if isnan(pp)
 eval(['p=',f,'_p;']);
 pp=p;
end
pp=(round(pp.*10))./10;
title(['BOREHOLE AM01 (2001/2002 season) microcat            ',f,' at pressure ',num2str(pp),' dbar'])
eval(['x1=min(',f,'_dectime);'])
eval(['x2=max(',f,'_dectime);'])
%axis([x1 x2 -2.1 -1.5]);
%axis([x1 x2 -2.1 1]); %for cat332
%axis([x1 x2 -2.1 0.5]); %for cat318,317
%axis([x1 x2 -1.0 2.7]); %for cat316
%axis([x1 x2 -2.1 1.0]); %for cat315
grid

subplot(412)
eval(['plot(',f,'_dectime,',f,'_cond)']);
ylabel('conductivity (mS/cm)')
%axis([x1 x2 27 28]);
%axis([x1 x2 27 30.5]); %for cat380
%axis([x1 x2 27.5 29.5]); %for cat318,317
%axis([x1 x2 27.5 30.0]); %for cat316
%axis([x1 x2 27.5 30.0]); %for cat315
grid

subplot(413)
eval(['plot(',f,'_dectime,',f,'_sal)']);
ylabel('salinity (PSS78)')
%axis([x1 x2 34.2 35]);
%axis([x1 x2 32.0 35]); %for cat332
%axis([x1 x2 34.0 35.3]); %for cat318,317,315
%axis([x1 x2 31.9 34.8]); %for cat316
grid

subplot(414)
eval(['plot(',f,'_dectime,',f,'_press)']);
xlabel('decimal days from January 1st 2001')
ylabel('pressure (dbar)')
%axis([x1 x2 34.2 35]);
%axis([x1 x2 32.0 35]); %for cat332
%axis([x1 x2 34.0 35.3]); %for cat318,317,315
%axis([x1 x2 31.9 34.8]); %for cat316
grid

%eval(['print -deps ',f,'.eps'])

clear f x1 x2 p m n pp
