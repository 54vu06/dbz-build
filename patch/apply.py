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
# 改用 bank 09 中與其圖組相符的調色盤（弗力札 09:D300：白底紫頂；基紐 09:D360：紫膚）
edit("crates/ssd-catalogue/src/art.rs", [
("""    let palette =
        rom.pointer(d::OBJECT_PORTRAIT_PALETTES + 2 * u32::from(palette_object), PALETTE_BANK)?;
    let half = u8::from(SECOND_FACE_PICTURES.contains(&face));""",
"""    let palette = match face {
        0x38 => 0x09_D300,
        0x31 => 0x09_D360,
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

# ---- 第三輪：弗力札、基紐頭像的原色（用 HD 美術包為該圖做的調色盤，不再套悟空的調色盤） ----
edit("crates/ssd-catalogue/src/art.rs", [
("    picture(rom, &set, (\"face_portrait_pointers\", face), palette, cells, half)\n}",
 """    let mut portrait = picture(rom, &set, ("face_portrait_pointers", face), palette, cells, half)?;
    if let Some(colours) = native_palette(face) {
        portrait.palette = colours;
    }
    Ok(portrait)
}

/// The colours the HD pack's art of a face was made in, for the extension's two faces (Frieza's final form, the second
/// picture of the set `16:BB4F`, and Captain Ginyu, the second picture of `16:B350`): the corner faces of the original
/// are drawn in one shared row, which would recolour their art.
fn native_palette(face: u8) -> Option<[u16; COLOURS]> {
    match face {
        0x38 => Some([
            0x0000, 0x0000, 0x6F7B, 0x2D6B, 0x627F, 0x0000, 0x4631, 0x3C87, 0x001F, 0x0000, 0x0000, 0x7FFF, 0x56B5,
            0x7B3B, 0x7914, 0x6890,
        ]),
        0x31 => Some([
            0x0000, 0x0000, 0x7B7F, 0x6659, 0x4D93, 0x390E, 0x013F, 0x43F6, 0x3373, 0x1F0F, 0x7FFF, 0x6739, 0x4210,
            0x1E64, 0x19C6, 0x6EFC,
        ]),
        _ => None,
    }
}"""),
])
print("patch OK")
