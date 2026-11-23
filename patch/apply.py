import sys, pathlib
root = pathlib.Path(sys.argv[1])

def edit(rel, pairs):
    p = root / rel
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if s.count(old) != 1:
            sys.exit(f"[patch 失敗] {rel} 找不到唯一的錨點:\n{old[:80]}")
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8", newline="")

edit("crates/ssd-catalogue/src/characters.rs", [
("/// The table of level caps (bank 3)",
 "/// Party extension: character ids 12, 13, 14 as `(unit id, level cap)` (12 = 0x54, 13 = 0x38 Frieza, 14 = 0x31 Ginyu).\n"
 "const EXTRA_CHARACTERS: [(u8, u8); 3] = [(0x54, 48), (0x38, 48), (0x31, 48)];\n\n"
 "/// The table of level caps (bank 3)"),
("    Ok(characters)\n}\n\n#[cfg(test)]",
 """    for (extra, &(unit_id, level_cap)) in EXTRA_CHARACTERS.iter().enumerate() {
        let id = count + u32::try_from(extra).expect("a few extras");
        let id8 = u8::try_from(id).expect("a dozen characters and a few");
        characters.push(Character {
            id: id8,
            name: table_name(rom, d::STRING_POINTERS, id)?,
            unit_id,
            levels: Vec::new(),
            fixed_stats_unit: Some(unit_id),
            level_cap,
        });
    }
    Ok(characters)
}

#[cfg(test)]"""),
("assert_eq!(characters.len(), 12);", "assert_eq!(characters.len(), 15);"),
])

edit("crates/ssd-catalogue/src/menus.rs", [
("const CHARACTER_FACES: [Option<u8>; 12] = [", "const CHARACTER_FACES: [Option<u8>; 15] = ["),
("    Some(0x61),\n];", "    Some(0x61),\n    None,\n    Some(0x38),\n    Some(0x31),\n];"),
])

p = root / "translations/zh-tw/zh-tw.tsv"
s = p.read_text(encoding="utf-8")
for k, v in (("13", "弗力札"), ("14", "基紐")):
    old = f"string:{k}\t卜卦婆婆\tnames_strings:{k} override"
    if s.count(old) != 1:
        sys.exit(f"[patch 失敗] tsv 找不到 string:{k}")
    s = s.replace(old, f"string:{k}\t{v}\tnames_strings:{k} override")
old = "object:24\t海龜\tnames_objects:24 override"
if s.count(old) != 1:
    sys.exit("[patch 失敗] tsv 找不到 object:24")
s = s.replace(old, "object:24\t青蛙\tnames_objects:24 override")
# 全遊戲「飛里沙」統一為「弗力札」（字數相同，不影響版面）
s = s.replace("飛里沙", "弗力札")
# 全遊戲「樂平」統一為「飲茶」（同為兩字，不影響版面）
assert s.count("樂平") == 6, s.count("樂平")
s = s.replace("樂平", "飲茶")
# 開場致謝頁：保留原字樣，下方加上第二組致謝（三行以內，每行最多 16 格，這裡取 15 格以內）
old = "str3:0x3E\t　　　　　　　　台式中文化\\n　　　Ｂｙ　Ｍｉｎｇ　Ｌｉｕ\tk3:62 split"
if s.count(old) != 1:
    sys.exit("[patch 失敗] tsv 找不到開場致謝 str3:0x3E")
s = s.replace(old, "str3:0x3E\t台式中文化，ＢｙＭｉｎｇＬｉｕ\\n魔改歡樂基紐、弗力札版，\\n　　　　　　ＢｙＡｃｈＬｅｅ\tk3:62 split")
p.write_text(s, encoding="utf-8", newline="")

edit("crates/ssd-catalogue/src/art.rs", [
("const SECOND_FACE_PICTURES: [u8; 5] = [0x09, 0x0A, 0x0C, 0x50, 0x61];",
 "const SECOND_FACE_PICTURES: [u8; 7] = [0x09, 0x0A, 0x0C, 0x50, 0x61, 0x38, 0x31];"),
])

# 弗力札(0x38)、基紐(0x31) 的角落頭像：原本一律套用物件 28（悟空）的調色盤 → 顏色錯誤。
# 改用 bank 09 中與其圖組相符的調色盤（弗力札 09:D300：白底紫頂；基紐 09:E300（使用者挑選））
edit("crates/ssd-catalogue/src/art.rs", [
("""    let palette =
        rom.pointer(d::OBJECT_PORTRAIT_PALETTES + 2 * u32::from(palette_object), PALETTE_BANK)?;
    let half = u8::from(SECOND_FACE_PICTURES.contains(&face));""",
"""    let palette = match face {
        0x38 => 0x09_D300,
        0x31 => 0x09_E300,
        _ => rom.pointer(d::OBJECT_PORTRAIT_PALETTES + 2 * u32::from(palette_object), PALETTE_BANK)?,
    };
    let half = u8::from(SECOND_FACE_PICTURES.contains(&face));"""),
])

edit("crates/ssd-menus/src/screens.rs", [
("""fn party(list: &mut DrawList, view: &MenuView) {
    for (member, &x) in view.party.iter().take(2).zip(CORNERS.iter()) {""",
"""fn party(list: &mut DrawList, view: &MenuView) {
    if view.party.len() > 2 {
        party_compact(list, view);
        return;
    }
    for (member, &x) in view.party.iter().take(2).zip(CORNERS.iter()) {"""),
("""/// Where the corner pictures of the field menu sit:""",
"""/// More than two members: small corner pictures, up to six down each side, the gauges beside each picture.
fn party_compact(list: &mut DrawList, view: &MenuView) {
    const SIDE: f32 = 56.0;
    const ROW: f32 = 64.0;
    const GAUGE: f32 = 104.0;
    const GAP: f32 = 8.0;
    for (index, member) in view.party.iter().take(12).enumerate() {
        let right = index % 2 == 1;
        let row = f32::from(u8::try_from(index / 2).unwrap_or(5));
        let y = CORNER_TOP + row * ROW;
        let x = if right { WIDTH - CORNER_INSET - SIDE - GAP - GAUGE } else { CORNER_INSET };
        let frame = Rect::new(x, y, SIDE, SIDE);
        list.push(Op::Portrait { rect: frame, picture: member.face.map(Picture::Face) });
        let gx = x + SIDE + GAP;
        gauge_row(
            list,
            GaugeRow { x: gx, y: y + 14.0, width: GAUGE, label: "HP", fill: palette::HP },
            (member.hp, member.max_hp),
        );
        gauge_row(
            list,
            GaugeRow { x: gx, y: y + 38.0, width: GAUGE, label: "KI", fill: palette::KI },
            (member.ki, member.max_ki),
        );
    }
}

/// Where the corner pictures of the field menu sit:"""),
])

# （第三輪「native_palette」已移除：改用 ROM 自己的 09:D300 / 09:E300 調色盤，見上方 art.rs 修改）
# ---- 第四輪：存檔格式改為本改版 ROM 的新版面（12 人隊伍使存檔變大），否則讀檔後道具袋綁不上 ----
# 本版 ROM：標頭 SRAM 32KB；存檔欄位起點 $0100/$0700/$0D00，每欄 $5D0（影像 $4D0 + 頁 $100），備份在 +$1400，
# 存檔標記在影像 +$4C0；道具狀態字 item_extra 由 7E:2BA0 搬到 7E:2C80（見 patchA2 的 7E 位址重新對映）。
edit("crates/ssd-save/src/lib.rs", [
("pub const SRAM_SIZE: usize = 0x2000;", "pub const SRAM_SIZE: usize = 0x8000;"),
("pub const SLOT_BASES: [usize; SLOT_COUNT] = [0x100, 0x600, 0xB00];", "pub const SLOT_BASES: [usize; SLOT_COUNT] = [0x100, 0x700, 0xD00];"),
("pub const SLOT_LEN: usize = 0x4F0;", "pub const SLOT_LEN: usize = 0x5D0;"),
("pub const BACKUP_OFFSET: usize = 0x1000;", "pub const BACKUP_OFFSET: usize = 0x1400;"),
("pub const IMAGE_LEN: usize = 0x3F0;", "pub const IMAGE_LEN: usize = 0x4D0;"),
("pub const MARK_OFFSET: usize = 0x3E0;", "pub const MARK_OFFSET: usize = 0x4C0;"),
("        if bytes.len() == SRAM_SIZE {", "        if bytes.len() >= SLOT_BASES[SLOT_COUNT - 1] + BACKUP_OFFSET + SLOT_LEN {"),
])
edit("re/symbols.toml", [("address = 0x7E2BA0", "address = 0x7E2C80")])

# ---- 第五輪：標題畫面不顯示「Select 編輯存檔」（作弊選單已涵蓋，且本改版的存檔格式與編輯器不相容）----
edit("crates/ssd-app/src/hd.rs", [
("        if self.editor.is_none()\n            && self.editor_allowed\n            && on_title(wram)",
 "        if self.editor.is_none()\n            && false\n            && self.editor_allowed\n            && on_title(wram)"),
("        if key == Key::ResetAll\n            && self.editor_allowed",
 "        if key == Key::ResetAll\n            && false\n            && self.editor_allowed"),
])

# ---- 第六輪：存檔選擇畫面不顯示「作弊（CHEATS）」標記 ----
edit("crates/ssd-game/src/menu/driver.rs", [
("                *mark = self.cheat_sidecar.marked(slot, checksum);",
 "                *mark = false && self.cheat_sidecar.marked(slot, checksum);"),
])

print("patch OK")
