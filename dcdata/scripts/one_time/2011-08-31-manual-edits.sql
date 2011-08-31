begin;

drop table if exists tmp_bios_to_delete;
create temp table tmp_bios_to_delete (entity_id uuid);

insert into tmp_bios_to_delete values
('027c7cd69f1b44d68a27863db118539f'),
('067b0d9ac8854e06b806db090b2851da'),
('0f14b8ef0e904dc6922135d3560e0f8c'),
('16d6ca8e31e64b8b92d03f339150c1dd'),
('18cd95e2684d42a5993de4523e2a6851'),
('1de02b6136f84ca88333ce2d28726018'),
('1dea6ed79fc04e3a8ca06ea53ef6071b'),
('1ff99b81a9be48c0ade105ad6cb18a7c'),
('211f71574d43447aa07c998d6a824a0d'),
('21ddf192177e443c9afcc623cad28451'),
('246a8667c4ec4c1f9f77c0b479ad595b'),
('25aeff7c2855460fa6594436349bd00f'),
('27c0d9ebe00d4cc0b9a985c089f02e41'),
('296c30d184844db2bc8869a081172979'),
('326dfca1df8e4a28b8f7d36e770c3333'),
('3465dc2fce1242c49f4e36997f6ca2f6'),
('350e0213445a45c8b0ef53de3538ee68'),
('35745d202e1b425b9d6a3542e5f4eb68'),
('3740a6cd670343bd8fed8f2fae356fec'),
('380ffdbe322d42219c8004552baa214f'),
('3b1bc09d7a3f4b1e902a22732c6c9746'),
('3d8ac442720847a98da5b1b8bcd6978f'),
('3ec40a65b07349b1ab84d6c0151b2f14'),
('406c8c8ccf8a40e4b5bdbb4dab65ac41'),
('412bd27bfda34beabf926932a54846f6'),
('42ba6ae3814c4e22934f1f3a91db9fb7'),
('44c5374517c74c5cb441210ff8387f81'),
('4509ac965bae4d1388d0b29a5b1d0548'),
('45d782e3aee040139e1df9a359d376c3'),
('462f541471ce44e280cac3a66d5b0799'),
('4c51fd59e39a4d4d89303ac6806766ec'),
('4e35ab8a7b5c4414a0960c55f99ac952'),
('4f47ab8953d04efd876d9102d439b2ea'),
('4ff8e36543f841ea9189d6ae81ac31a4'),
('51196451b6744843b405feb407483efb'),
('517abf2fddfb4e4eaab282aa056f7805'),
('5246c8d8c76d4f78b6c88b6ba893e550'),
('52c39fc5205049488558c1603aaa7664'),
('55769dc059f447509413f516ce4bd05e'),
('590976a0edb94784a916bad895954766'),
('598f2a9ace7a4d2ab2ccc130c6fd5c29'),
('59bad53b8b744009949ecf56b4ae113f'),
('59bd8657e4144805b686a53e5360122b'),
('59e80dc2124a44f9b8507336fb412582'),
('5a625f9c5dee46068e7251f4fcfe775a'),
('5a7a9590759f463ba771a388934726b6'),
('613b383d682c4a048560a490e6b5ede5'),
('61bf4a4dafc6411ab4fb04848a137573'),
('62ca591ba17f40d7869a138aee61dd3c'),
('644115fb26eb44b9bbb894bfd12dbaa9'),
('64fd6aa67eac4ef8ac3219d9120abe45'),
('655de4257c5d47228cd7e46954abdabb'),
('69a98edb46774531a9b78d5dd034d5a5'),
('6ab8a1f1868a4fd6bda1b7f02638bb60'),
('6b4429d95b90466e8e9822bd80508d7b'),
('6b8951d4951f40e5a3603e04e1c05da9'),
('6c2119baaff5478f88221373884eb652'),
('6efd5d4c5cfc4908a51afc6200a62e60'),
('7005d36fe5b74b388a2e358e3e7508fc'),
('72017754e9794dd99bd523c6fb19db40'),
('7239ad10386d46caa807bac568c5a1ba'),
('73dd03f2527c4461b8d7115aba5b825d'),
('741ac400314945a28dbd40dd3382fef8'),
('7448fda112cf4b7d8cac977c35397d37'),
('75c0f0b208064ff7a7e4b8b7231f26aa'),
('7823dc2d0dfd4c9e9da8e489fb17001f'),
('7823f4a4bb874964b7986af77d7eaf52'),
('797db210f41944d0b045c7d90343f4be'),
('7b1c8b84c6384b848dad463936f8f4d3'),
('7bf2ff6c5bd949f99127208911adf9d4'),
('7d6ad43570d34622932761ca2ae2c31e'),
('7f63dd60986e44b4a4141320b636fb96'),
('80691fba00c144d39295e60d13f61e3b'),
('8563476380d64b85817e7070139f60b2'),
('86c7d0f46eaa4535b91a081925cd38db'),
('87d8c8bc93104357a621b32942bbe3f1'),
('8d64c31b5f3a4ca6846bec6766f0b304'),
('8f29b34cce4a4884ababfe498a6ea337'),
('91dbce631850416f9e000cdb0113734a'),
('9353fc663e774a7b887a9ec86cdf4747'),
('9559a3a5afa043319f8963996b3c15c0'),
('989e70a1229d45958ee6dc5120639170'),
('99efa080ef0645dfaa1dafbea9b4c562'),
('9de47d0c52a24f0599ad5bf44b7d14ad'),
('9dea3e73a62b4158b59b90ab20ae6be5'),
('ab97a014d00a4c1cbf89193bc52742cc'),
('ac70618cc5294b24a6882995b138446b'),
('ade9872639784b4a917972378fcdf702'),
('ae9c52823eaa4372b189f196967e1034'),
('b19aeea748754ed49977bf3047bc1cb6'),
('b386ce44031c4a90a725184067ed8248'),
('b412a207cfce4fc8a0d01d9bfd0efd79'),
('b8b5ee57725046e0ba341e5adb8c1b97'),
('bb03dec8bfb64da29b67644234a34a65'),
('bee42c44120147239115361f2a605169'),
('bf95fc00b84b47cfbf92b2d5941c52c0'),
('c0407a808b504ec2940fd338dd759a13'),
('c133d129ad034dc3a001028604d218f7'),
('c13f980752ef427ca30ee13df6993203'),
('c29881d7e1f241e78588d48a5b11561e'),
('c584776443c74c5f849dcc1b9c757374'),
('c9ff6e3e22154dcaa402cf52324a51be'),
('ca81bd035b5345b28fac0c43ee32ba99'),
('cbe740a61d044e31a3efe04990f464ab'),
('cfe5ebc457c2464aa4f5ce490b6b87e1'),
('d112ca4b8758484f8d1384edf9381925'),
('d360ad9a11214981bd75e733a575e223'),
('d9b40e5c55d54f8ab961444a8507e56e'),
('da0c20012a244738bb5052d50713066a'),
('dcd3d1a59ad84755a75a36d26bdf9d29'),
('df45766fc5244d9cb62283bce20c1a10'),
('e05da97dfd494a7898fb596985e24040'),
('e31b3246c91a4665824c34105523df88'),
('e8a7b5c1c6a94b798af31a238b50a227'),
('e8ba2f2a16cf4bb2859813b5221fdd8d'),
('ea5d64dac20e4364a76b686899d06e09'),
('eac760245c104fb9b59318cd89e3d1e0'),
('ecb87a9fd4b04809b9fadd5b712f9569'),
('ee035bd690c1492cbb14c801bf3a1a6d'),
('f3d41084e157467090a1fde0ed9d923a'),
('f3edbcf74dba48f1a4140fcf662fe8dd'),
('f6eda0e61ffb47c38f3160c27716e9ec'),
('f8fa52d391dc48198e60712e102a2d6a'),
('fa763b3ec5884e45a75648b7d3c7562b'),
('fc97ff7446bc4955adb4b9650f5e8285'),
('fd66e6abb51f4fb2ab505c64a99e808c'),
('01a7f2cbb1754ad7972ce310e52ece93'),
('031c88583d0442508f7926991f6215dd'),
('03a985edc585463285ce289f8a1b2bf9'),
('04293dc7218248ca978b73a614f52ed9'),
('053ad0961e2547f2a548ca0e508e62e4'),
('05df87fa68984ecb8a58db6addd6c245'),
('087d960b2b984df78b524fad71dd48b6'),
('09765a49382e475f9b466f782fb8c35d'),
('0a72b340409f483facc325d73635e1f3'),
('0b10bca9e06d43a1b487acc51ab5782a'),
('0c2db6c48521420abdda8465bef6395b'),
('0d2135d9279a417b87e89ae5f6b44a3d'),
('0dfa39f376704ac5a52f321065503dd2'),
('0e02afd55c8542608607e7b37d068f86'),
('0e30c7bb873245a094b005650d37d724'),
('0f1fed329e0840f298f58c6ddb9b23cb'),
('0faeba6c76e244d1826046390e9e6a17'),
('117ab871072e47689857b05d1b9f2dbe'),
('1355eb87e1364b459945eb25470d44ae'),
('13a1943112804132b290b558cab4c6e5'),
('13d3a2c9796746d28b9c8de9b264572a'),
('13eafd84a3b94452b102f0e0fc97a09d'),
('154cdae1f14f459db383d226a9c54f54'),
('0b2741f2e5274f4eb5f8428155ef61c5');

delete from matchbox_sunlightinfo
where entity_id in (select * from tmp_bios_to_delete);

insert into matchbox_sunlightinfo (entity_id, bio, photo_url)
select entity_id, '', '' from tmp_bios_to_delete;

commit;