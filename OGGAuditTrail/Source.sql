-- This script should be executed on source DB as user with appropriate permissions
-- Tested for Oracle DB 19c, adapt for other DB and version as required
-- ORA-00942: table or view does not exist  errors are expected and can be ignored
-- Replace xxxx with actual passwords
-- replace dwrole with equivalent role for non Oracle autonomous databases

Drop user AppOwner cascade;
Drop user Calvin cascade;
Drop user Susie cascade;
Drop user Hobbes cascade;
-- USER SQL
CREATE USER AppOwner no authentication DEFAULT TABLESPACE DATA TEMPORARY TABLESPACE TEMP;
CREATE USER Susie identified by "xxxx" DEFAULT TABLESPACE DATA TEMPORARY TABLESPACE TEMP;
CREATE USER Calvin identified by "xxxx" DEFAULT TABLESPACE DATA TEMPORARY TABLESPACE TEMP;
CREATE USER Hobbes identified by "xxxx" DEFAULT TABLESPACE DATA TEMPORARY TABLESPACE TEMP;
-- QUOTAS
ALTER USER AppOwner QUOTA UNLIMITED ON DATA;
grant connect,dwrole to appowner;
alter user AppOwner grant connect through Susie,calvin,hobbes,admin;
grant connect,create session to calvin,Susie,hobbes;
drop table APPOWNER.emp;
  CREATE TABLE APPOWNER.EMP 
   (	EMPNO VARCHAR2(20 BYTE)  NOT NULL ENABLE, 
	EMP_NAME VARCHAR2(20 BYTE) , 
	DESIGNATION VARCHAR2(20 BYTE) , 
	DEPARTMENT VARCHAR2(20 BYTE) , 
	SALARY NUMBER, 
	DOB DATE, 
	HOMECOUNTRY VARCHAR2(20 BYTE) , 
	WORKCOUNTRY VARCHAR2(20 BYTE) , 
	STATUS VARCHAR2(20 BYTE)  NOT NULL ENABLE, 
	 CONSTRAINT EMP_PK PRIMARY KEY (EMPNO)  USING INDEX    )  ;

--  DDL for Table DEPARTMENT

drop table appowner.department;
  CREATE TABLE APPOWNER.DEPARTMENT 
   (	DEPTNO NUMBER NOT NULL ENABLE, 
	DEPTNAME VARCHAR2(20 BYTE) , 
	LOB VARCHAR2(20 BYTE) , 
	COUNTRY VARCHAR2(20 BYTE) , 
	COSTCENTER VARCHAR2(20 BYTE) , 
	 CONSTRAINT DEPARTMENT_PK PRIMARY KEY (DEPTNO)  USING INDEX ENABLE
   ) ;

TRUNCATE TABLE appowner.DEPARTMENT;
TRUNCATE TABLE appowner.EMP;
grant all on appowner.department to calvin,susie,hobbes;
grant all on appowner.emp to calvin,Susie,hobbes;
