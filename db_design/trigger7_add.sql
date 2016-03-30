--description: 16. The current time of your AuctionBase system can only advance forward in time, not backward in time.

PRAGMA foreign_keys = ON;
drop trigger if exists time_advance_trig;
create trigger time_advance_trig
before update on CurrentTime
for each row
when exists (
	select *
	from CurrentTime c
	where c.C_Time >= new.C_Time
)
begin
  select raise(rollback,"Time must advance forward");
end;