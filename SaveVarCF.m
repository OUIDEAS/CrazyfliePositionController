%%
%Data import

clc; close all; 
% importdata('THT_DATA_3_3.txt', ', '); 

close all;
clear VarName12 VarName15 VarName18 VarName21 VarName3 VarName6 VarName9
clear VarName24 VarName27 VarName30 VarName33 VarName36 VarName39 VarName42
clear VarName45 VarName48 VarName51 VarName54 VarName57 VarName60
clear time velocity x y z x_sp y_sp z_sp yaw_sp
clear X_acc Y_acc Z_acc
clear Pitch Roll Thrust Pitch_cmd Roll_cmd Thrust_cmd yaw Yaw_CF Yaw_cmd

time=VarName2;
x=VarName5; y=VarName8; z=VarName11; yaw=VarName14; velocity=VarName17;
x_sp=VarName20; y_sp=VarName23; z_sp=VarName26; yaw_sp=VarName29; 
Roll_cmd=VarName32; Pitch_cmd=VarName35; Thrust_cmd=VarName38; Yaw_cmd=VarName41;
Roll=NaN1; Pitch=NaN2; Yaw_CF=NaN3; Thrust=NaN4; X_acc=NaN5; Y_acc=NaN6; Z_acc=NaN7;

clear VarName*  NaN*
%% 
%Plots
figure;
x_sp(1:200)=x(1); y_sp(1:200)=y(1); z_sp(1:200)=z(1);
plot3(x,y,z,'r',x_sp,y_sp,z_sp,'b--*');
xlabel('x (m)'); ylabel('Y (m'); zlabel('Z (m)'); grid;

figure;
yaw=yaw*180/pi; yaw_CF=Yaw_CF-Yaw_CF(200)+yaw(1);
plot(time,yaw,'r-',time,yaw_sp,'b--',time,yaw_CF,'k-.'); grid;
xlabel('time (s)'); ylabel('Yaw (deg)'); 
legend('Vicon','Set Point','CF');

figure;
plot(time,Roll_cmd,'b--',time,Roll,'r-'); grid;
xlabel('time (s)'); ylabel('Roll (deg)');

figure;
plot(time,-Pitch_cmd,'b--',time,Pitch,'r-'); grid;
xlabel('time (s)'); ylabel('Pitch (deg)');

% figure;
% %Thrust_cmd=mapfun(Thrust_cmd,0,100,0,65535);
% plot(time,Thrust_cmd,'b--',time,Thrust,'r:'); grid; 
% xlabel('time (s)'); ylabel('Thrust (16 bit)');

figure;
plot(time,X_acc,time,Y_acc,time,Z_acc); grid;
xlabel('time (s)'); ylabel('Acceleration');
legend('X','Y','Z');


figure; 
subplot(311);
plot(time,x,'r-',time,x_sp,'b--');
xlabel('time (s)'); ylabel('x (m)'); grid;
subplot(312);
plot(time,y,'r-',time,y_sp,'b--');
xlabel('time (s)'); ylabel('y (m)'); grid;
subplot(313); 
plot(time,z,'r-',time,z_sp,'b--');
xlabel('time (s)'); ylabel('z (m)'); grid;