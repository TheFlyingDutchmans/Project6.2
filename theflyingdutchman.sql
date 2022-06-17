-- phpMyAdmin SQL Dump
-- version 4.9.5deb2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Jun 15, 2022 at 01:32 PM
-- Server version: 8.0.29-0ubuntu0.20.04.3
-- PHP Version: 7.4.3

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `theflyingdutchman`
--

-- --------------------------------------------------------

--
-- Table structure for table `requests`
--

CREATE TABLE `requests` (
  `requestID` int NOT NULL,
  `userID` int NOT NULL,
  `shipID` int NOT NULL,
  `longitude` float NOT NULL,
  `latitude` float NOT NULL,
  `timestamp` int NOT NULL,
  `cog` int NOT NULL,
  `sog` int NOT NULL,
  `heading` int NOT NULL,
  `rot` int NOT NULL,
  `status` int NOT NULL,
  `currentTime` timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `requests`
--

INSERT INTO `requests` (`requestID`, `userID`, `shipID`, `longitude`, `latitude`, `timestamp`, `cog`, `sog`, `heading`, `rot`, `status`, `currentTime`) VALUES
(8, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, '2022-06-07 09:48:47.306555'),
(9, 40, 24, 42, 19, 44, 171, 58, 322, 2, 7, '2022-06-07 10:24:02.649829'),
(10, 39, 4, -17, 80, 54, 0, 96, 77, -50, 0, '2022-06-07 10:24:02.650414'),
(11, 49, 40, 96, -85, 15, 99, 35, 107, 18, 3, '2022-06-07 10:24:02.650698'),
(12, 19, 37, -80, 75, 28, 170, 32, 288, -54, 0, '2022-06-07 10:24:02.650972'),
(13, 3, 32, 27, 60, 10, 128, 43, 118, 38, 7, '2022-06-07 10:24:02.651288'),
(14, 41, 27, 177, -21, 0, 28, 99, 170, -85, 15, '2022-06-07 10:24:02.651567'),
(15, 16, 24, 165, -83, 24, 117, 30, 1, 23, 3, '2022-06-07 10:24:02.651792'),
(16, 3, 42, -100, 34, 46, 162, 74, 345, 123, 1, '2022-06-07 10:24:02.651988'),
(17, 1, 47, 16, 40, 36, 116, 71, 104, -27, 15, '2022-06-07 10:24:02.652183'),
(18, 36, 1, -116, -13, 57, 128, 84, 91, 33, 0, '2022-06-07 10:24:02.652462'),
(19, 9, 12, -10, -36, 33, 90, 29, 149, 103, 15, '2022-06-07 10:24:02.652717'),
(20, 35, 44, -35, 71, 36, 173, 52, 60, 75, 1, '2022-06-07 10:24:02.652947'),
(21, 50, 42, -98, -46, 53, 120, 99, 338, -86, 3, '2022-06-07 10:24:02.653195'),
(22, 39, 0, 139, 65, 31, 160, 30, 344, -47, 3, '2022-06-07 10:24:02.653447'),
(23, 46, 15, -32, 47, 60, 161, 22, 97, -71, 7, '2022-06-07 10:24:02.653696'),
(24, 32, 49, -32, 78, 33, 22, 44, 142, -36, 1, '2022-06-07 10:24:02.653943'),
(25, 11, 10, 119, -28, 23, 105, 49, 43, 127, 1, '2022-06-07 10:24:02.654162'),
(26, 38, 5, 57, -62, 10, 83, 22, 260, -23, 15, '2022-06-07 10:24:02.654410'),
(27, 3, 37, -24, 46, 52, 123, 61, 335, 120, 3, '2022-06-07 10:24:02.654656'),
(28, 25, 15, 150, 38, 10, 27, 99, 250, 28, 15, '2022-06-07 10:24:02.654902'),
(29, 32, 26, 65, -22, 44, 135, 16, 9, -108, 3, '2022-06-07 10:24:02.655145'),
(30, 50, 41, 10, 14, 15, 154, 93, 104, 17, 3, '2022-06-07 10:24:02.655391'),
(31, 19, 3, 146, 84, 39, 131, 55, 14, 53, 1, '2022-06-07 10:24:02.655634'),
(32, 16, 16, 138, 28, 24, 178, 22, 219, -125, 1, '2022-06-07 10:24:02.655847'),
(33, 21, 1, 82, -1, 2, 33, 28, 40, 11, 0, '2022-06-07 10:24:02.656092'),
(34, 33, 19, 46, -58, 52, 47, 79, 219, 6, 3, '2022-06-07 10:24:02.656335'),
(35, 47, 48, 12, 13, 53, 163, 53, 260, -14, 7, '2022-06-07 10:24:02.656546'),
(36, 10, 21, 109, 80, 30, 9, 24, 149, 104, 3, '2022-06-07 10:24:02.656788'),
(37, 26, 44, -12, -29, 36, 53, 45, 308, -123, 1, '2022-06-07 10:24:02.657049'),
(38, 17, 8, -112, 90, 4, 36, 93, 17, -52, 3, '2022-06-07 10:24:02.657297'),
(39, 40, 36, -14, 35, 43, 35, 37, 342, -61, 1, '2022-06-07 10:24:02.657543'),
(40, 14, 50, 92, -25, 11, 44, 60, 134, 56, 15, '2022-06-07 10:24:02.657761'),
(41, 46, 47, 175, -21, 5, 180, 17, 290, 99, 0, '2022-06-07 10:24:02.658003'),
(42, 8, 37, -133, -40, 15, 27, 30, 215, 28, 3, '2022-06-07 10:24:02.658214'),
(43, 25, 18, -57, 21, 3, 33, 41, 35, -75, 15, '2022-06-07 10:24:02.658456'),
(44, 47, 18, 44, -64, 20, 25, 97, 235, 108, 3, '2022-06-07 10:24:02.658696'),
(45, 50, 33, 104, -53, 54, 148, 85, 130, 42, 0, '2022-06-07 10:24:02.658934'),
(46, 33, 10, -142, -35, 37, 51, 56, 311, 126, 1, '2022-06-07 10:24:02.659145'),
(47, 19, 8, -73, -36, 16, 92, 48, 100, 116, 7, '2022-06-07 10:24:02.659385'),
(48, 23, 11, -76, -75, 38, 75, 92, 136, 23, 7, '2022-06-07 10:24:02.659595'),
(49, 6, 44, -47, -43, 27, 8, 99, 102, -123, 0, '2022-06-07 10:24:02.659874'),
(50, 47, 49, -23, -29, 53, 140, 20, 153, 20, 0, '2022-06-07 10:24:02.660123'),
(51, 49, 26, -41, -67, 18, 20, 44, 275, 27, 0, '2022-06-07 10:24:02.660441'),
(52, 16, 46, 87, -59, 46, 78, 41, 221, -110, 7, '2022-06-07 10:24:02.660688'),
(53, 22, 41, 142, 27, 11, 161, 42, 230, -9, 7, '2022-06-07 10:24:02.660973'),
(54, 20, 46, 92, -63, 28, 58, 20, 135, -71, 0, '2022-06-07 10:24:02.661216'),
(55, 14, 15, 51, -85, 29, 44, 30, 283, -33, 0, '2022-06-07 10:24:02.661477'),
(56, 0, 3, 139, -43, 14, 105, 57, 168, 47, 3, '2022-06-07 10:24:02.661682'),
(57, 48, 48, -41, -14, 40, 115, 68, 74, -76, 3, '2022-06-07 10:24:02.661936'),
(58, 34, 21, 8, 54, 39, 136, 51, 214, -90, 3, '2022-06-07 10:24:02.662252');

-- --------------------------------------------------------

--
-- Table structure for table `shipstatic`
--

CREATE TABLE `shipstatic` (
  `shipID` int NOT NULL,
  `mmsi` int NOT NULL,
  `nameOfShip` varchar(20) NOT NULL,
  `typeOfShip` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `shipstatic`
--

INSERT INTO `shipstatic` (`shipID`, `mmsi`, `nameOfShip`, `typeOfShip`) VALUES
(1, 201123456, 'Grand Jolly', 12),
(2, 701647225, 'Edwin', 41),
(3, 201513229, 'Ricardo', 40),
(4, 668126875, 'Jerry', 42),
(5, 356138275, 'Connie', 39),
(6, 361767108, 'Martin', 26),
(7, 310611892, 'Adam', 89),
(8, 212136953, 'Michael', 28),
(9, 720915808, 'Karl', 97),
(10, 631279268, 'Aaron', 58),
(11, 312393650, 'David', 99),
(12, 436717300, 'Tiffany', 87),
(13, 565422919, 'Derek', 15),
(14, 262420729, 'Maria', 79),
(15, 332817912, 'Jeremy', 73),
(16, 661639126, 'Kenneth', 40),
(17, 374100974, 'Rebecca', 73),
(18, 219336104, 'Dustin', 15),
(19, 679283897, 'Carla', 14),
(20, 263825622, 'Darrell', 14),
(21, 477824967, 'Lucas', 13),
(22, 475956644, 'Jennifer', 80),
(23, 765559423, 'Patrick', 87),
(24, 249378573, 'Carol', 37),
(25, 765148280, 'William', 84),
(26, 273640243, 'Anthony', 56),
(27, 202640276, 'Cory', 71),
(28, 642264669, 'Jesus', 60),
(29, 725547935, 'Kristin', 83),
(30, 234291219, 'Miranda', 57),
(31, 314495971, 'Gregory', 66),
(32, 244505975, 'Sarah', 88),
(33, 679150591, 'Glenn', 35),
(34, 277623204, 'Diamond', 40),
(35, 254268493, 'Thomas', 58),
(36, 269726273, 'Kathleen', 30),
(37, 625205780, 'Tammie', 81),
(38, 266245403, 'Tyler', 63),
(39, 566522696, 'Wanda', 97),
(40, 334353680, 'Shannon', 63),
(41, 508697520, 'Matthew', 85),
(42, 557534455, 'Courtney', 38),
(43, 225177581, 'Meghan', 93),
(44, 301747909, 'Amanda', 13),
(45, 536738878, 'Robert', 22),
(46, 258828255, 'Tammy', 88),
(47, 508326786, 'Alan', 84),
(48, 512296427, 'Todd', 42),
(49, 663212343, 'John', 77),
(50, 657908745, 'Mariah', 86),
(51, 215403697, 'Sergio', 35),
(52, 333333333, 'Grand Jolly', 12);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `userID` int NOT NULL,
  `apiKey` varchar(50) NOT NULL,
  `apiLimit` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`userID`, `apiKey`, `apiLimit`) VALUES
(1, 'admin', 994),
(2, 'FduRVG4WvL8UkNfotgVFamN792hzE0CwW0NvQNfmVaTf6zlsml', 701),
(3, 'ywL23r4JU7rfYo4Hvjxkk19IkXP4Ati8M5rSmbm1zeSIDz654n', 649),
(4, 'rC0BxdfhKTE61lSBG6FeLIKhviJejUAZnYmKnyBMZgr7pOzoXt', 394),
(5, 'fl4b7qMzuoG1m0LcG1fKXKM5dxK0oa0PBMhFedu4OjfphXrcic', 604),
(6, 'eLG2BZr1Xps1b3PpP8kNzzUa1CGvvLKd0H2IJF75f4qnZakHQS', 365),
(7, 'xyQoZQo2rcaElTPuoTR5eyAAZi9dzoMuNCuSu72qBxqdvsY8BW', 975),
(8, 'oAJsoJwtHkU9uUrt9wgcOKUN47FJve2Ki2bgk0fVYJV0xCzj5e', 867),
(9, '87ryknFns0MtZJqd3zmyY4ts0W7PZbB0gL5KOQMqIbIMYh40JR', 970),
(10, 'sOHVHPgela6DY6ZiLTW5FfYjVEWcukBY204tcumje8iEE8wu8k', 606),
(11, 'av7YaGijhQo6kxIJ4LMSFjX4xxlZUGaHsytqypR7TSLAaktlaw', 591);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `requests`
--
ALTER TABLE `requests`
  ADD PRIMARY KEY (`requestID`);

--
-- Indexes for table `shipstatic`
--
ALTER TABLE `shipstatic`
  ADD PRIMARY KEY (`shipID`),
  ADD UNIQUE KEY `mmsi` (`mmsi`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`userID`),
  ADD UNIQUE KEY `apiKey` (`apiKey`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `requests`
--
ALTER TABLE `requests`
  MODIFY `requestID` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=59;

--
-- AUTO_INCREMENT for table `shipstatic`
--
ALTER TABLE `shipstatic`
  MODIFY `shipID` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=53;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `userID` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
