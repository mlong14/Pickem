

drop table if exists Results;
drop table if exists Picks;
drop table if exists Users;
drop table if exists Contestants;
drop table if exists Events;
drop table if exists Entries;

create table Results(
	EventID int PRIMARY KEY,
	First int,
	Second int,
	Third int,
	Fourth int,
	foreign key(EventID) references Events(EventID),
	foreign key(First) references Contestants(AthID),
	foreign key(Second) references Contestants(AthID),
	foreign key(Third) references Contestants(AthID),
	foreign key(Fourth) references Contestants(AthID)
);

create table Picks(
	UserID int,
	EventID int,
	First int,
	Second int,
	Third int,
	Fourth int,
	foreign key(UserID) references Users(UserID)
	foreign key(EventID) references Events(EventID),
	foreign key(First) references Contestants(AthID),
	foreign key(Second) references Contestants(AthID),
	foreign key(Third) references Contestants(AthID),
	foreign key(Fourth) references Contestants(AthID),
	UNIQUE(UserID,EventID)
	);

create table Users(
	UserID int,
	UserName varchar(255) PRIMARY KEY,
	Eligible boolean,
	Unique(UserID)
);

create table Contestants(
	AthID int,
	AthName varchar(255) PRIMARY KEY,
	Unique(AthID)
);

create table Events(
	EventID int,
	EventName varchar(255) PRIMARY KEY,
	Unique(EventID)
);

create table Entries(
	EventID int,
	AthID int,
	foreign key(EventID) references Events(EventID),
	foreign key(AthID) references Contestants(AthID)
);
