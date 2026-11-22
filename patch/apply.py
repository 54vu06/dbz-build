
# ---- 第二輪修正 ----
edit("crates/ssd-catalogue/src/art.rs", [
("const SECOND_FACE_PICTURES: [u8; 5] = [0x09, 0x0A, 0x0C, 0x50, 0x61];",
 "const SECOND_FACE_PICTURES: [u8; 7] = [0x09, 0x0A, 0x0C, 0x50, 0x61, 0x38, 0x31];"),
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

p = root / "translations/zh-tw/zh-tw.tsv"
s = p.read_text(encoding="utf-8")
old = "object:24\t海龜\tnames_objects:24 override"
if s.count(old) != 1:
    sys.exit("[patch 失敗] tsv 找不到 object:24")
s = s.replace(old, "object:24\t青蛙\tnames_objects:24 override")
p.write_text(s, encoding="utf-8", newline="")
print("patch2 OK")
