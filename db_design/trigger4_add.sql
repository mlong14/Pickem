--description: 13. In every auction, the Number of Bids attribute corresponds to the actual number of bids for that particular item.

PRAGMA foreign_keys = ON;
drop trigger if exists num_bid_trig;
create trigger num_bid_trig
after insert on Bid
for each row
begin
  update Item set BidCount = BidCount + 1 where
  ItemID = new.ItemID;
end;