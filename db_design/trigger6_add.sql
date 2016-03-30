--description: 15. All new bids must be placed at the time which matches the current time of your AuctionBase system.

PRAGMA foreign_keys = ON;
drop trigger if exists time_of_bid_trig;
create trigger time_of_bid_trig
before insert on Bid
for each row
when not exists (
	select *
	from CurrentTime c
	where c.C_Time = new.Time
)
begin
  select raise(rollback,"Bid time needs to match curent time");
end;