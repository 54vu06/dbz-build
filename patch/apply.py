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
p.write_text(s, encoding="utf-8", newline="")
print("patch OK")
