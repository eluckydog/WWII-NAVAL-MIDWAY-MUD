#!/usr/bin/env python3
"""
Midway Night Battle — WWII Naval Tactical MUD.
Language auto-detect: type in Chinese → full Chinese. English → full English.
Mode select

ion at startup.
"""
import sys, os, math, random, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/monte_carlo')
import battle as bt
import engine as mc
import buffs

# Chinese ship name map
CN_NAME = {
    "iowa": "衣阿华号",
    "south_dakota": "南达科他号",
    "nagato": "长门",
    "mutsu": "陆奥",
    "kongo": "金刚",
    "haruna": "榛名",
    "yukikaze": "雪风",
    "kagero": "阳炎",
    "isokaze": "矶风",
    "shiranui": "不知火",
    "kuroshio": "黑潮",
}

def cn_name(ship):
    """Return Chinese name for a ship by key or name field."""
    if isinstance(ship, str):
        return CN_NAME.get(ship, ship)
    key = ship.get("_key", "")
    if key and key in CN_NAME:
        return CN_NAME[key]
    return ship.get("name", "?")



# ============================================================
# LANGUAGE HELPERS
# ============================================================

def has_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff\u3400-\u4dbf]', text))

def t(key, cn, **kw):
    val = LANG.get(key)
    if not val:
        return key
    if isinstance(val, tuple):
        txt = val[0] if cn else val[1]
    elif isinstance(val, list):
        txt = random.choice(val)
    else:
        txt = val
    if kw:
        try:
            txt = txt.format(**kw)
        except KeyError:
            pass
    return txt


# ============================================================
# SHIP CLASS NAMES (for radar display)
# ============================================================

def classify_ship(s, cn=True):
    """Return (short_name, type_label) for a ship dict."""
    if cn:
        nm = cn_name(s.get("_key", ""))
    else:
        nm = s.get("name", "?")
    if s.get("displacement", 0) > 10000:
        return (nm, "战列舰" if cn else "Battleship")
    else:
        return (nm, "驱逐舰" if cn else "Destroyer")


# ============================================================
# LOCALIZATION
# ============================================================

LANG = {
    "adj_intro": (
        "你的副官站在身侧——海军上校阿利·伯克，手持《太平洋舰队交战条例》和笔记本。",
        "Your adjutant stands at your side — Captain Arleigh Burke, regulations manual and notepad in hand."
    ),
    "adj_01": (
        "第47条：进入炮击距离前应保持队列紧密。南达科他号在您后方。",
        "Article 47: maintain tight formation before entering gun range. South Dakota is astern."
    ),
    "adj_norm_01": (
        "副官核对手表：「南达科他号跟在后面，距离正常。」",
        "Adjutant: 'South Dakota is right behind us, normal interval.'"
    ),
    "adj_radar_down": (
        "条例第82条：雷达离线期间减速至巡航航速，加强瞭望。",
        "Article 82: during radar outage, reduce to cruising speed, double lookouts."
    ),
    "adj_norm_radar_down": (
        "副官：「雷达没了。我让瞭望员瞪大眼睛。」",
        "Adjutant: 'Radar's out. Lookouts are on it.'"
    ),
    "adj_radar_restored": (
        "条例第83条：雷达恢复，信号清晰。",
        "Article 83: radar restored. Signals clear."
    ),
    "adj_norm_radar_restored": (
        "副官：「雷达回来了。能看清了。」",
        "Adjutant: 'Radar's back. We can see them.'"
    ),
    "adj_quiet": (
        ".",
        "."
    ),
    "adj_norm_quiet": (
        "副官保持沉默。海图室里只有钟声。",
        "The adjutant is quiet. Only the chronometer ticks."
    ),
    "adj_hit": (
        "命中。我方弹着点覆盖概位，跨射形成。继续保持射速。",
        "Hit confirmed. Salvos straddling target. Maintain rate of fire."
    ),
    "adj_norm_hit": (
        "副官：「打中了！」",
        "Adjutant: 'We got 'em!'"
    ),
    "adj_hit_second": (
        "命中多发。敌舰上层结构观测到火光。",
        "Multiple hits. Fires observed on enemy superstructure."
    ),
    "adj_norm_hit_second": (
        "副官：「又中了！他们着火了！」",
        "Adjutant: 'Another hit! They're on fire!'"
    ),
    "adj_taking_fire": (
        "中弹！损害管制组就位——报告损情！",
        "Hit taken! Damage control parties to stations — report casualties!"
    ),
    "adj_norm_taking_fire": (
        "船体一震。副官抓住海图桌边缘：「我们中弹了！」",
        "The hull shudders. The adjutant grabs the chart table: 'We're hit!'"
    ),
    "adj_fire": (
        "起火。损管组已就位，灭火作业实施中。",
        "Fire. Damage control parties responding, firefighting in progress."
    ),
    "adj_norm_fire": (
        "副官：「开始冒烟了！损管队在灭火。」",
        "Adjutant: 'Smoke! Damage control's on it.'"
    ),
    "adj_flood": (
        "进水！抽水机全开。",
        "Flooding! Pumps at maximum."
    ),
    "adj_norm_flood": (
        "副官：「水涌进来了！抽水机在工作。」",
        "Adjutant: 'We're taking water! Pumps are running.'"
    ),
    "adj_list": (
        "舰体侧倾{}度。右舷注水进行平衡调整。",
        "List {} degrees. Counter-flooding starboard to correct."
    ),
    "adj_norm_list": (
        "副官：「船在歪！倾斜{}度了。」",
        "Adjutant: 'She's listing! {} degrees.'"
    ),
    "adj_sodak_down": (
        "长官……南达科他号失去联系。",
        "Sir... South Dakota has gone silent."
    ),
    "adj_norm_sodak_down": (
        "副官低声说：「南达科他号……没回应了。」",
        "Adjutant, quietly: 'South Dakota... no response.'"
    ),
    "adj_night": (
        "夜战——能见度受限。注意规避航向变化。",
        "Night engagement — limited visibility. Watch for course changes."
    ),
    "adj_norm_night": (
        "副官：「天黑看不见什么。靠雷达了。」",
        "Adjutant: 'Can't see much in this dark. Radar's our eyes.'"
    ),
    "adj_radar_contact": (
        "雷达接触：{name}，{cls}，方位概略{brg:.0f}度，距离{d:.1f}公里。",
        "Radar contact: {name}, {cls}, bearing approx {brg:.0f}, range {d:.1f}km."
    ),
    "adj_norm_radar_contact": (
        "雷达上看到一艘：{name}（{cls}），大约在右前方{d:.1f}公里。",
        "Radar shows one: {name} ({cls}), about {d:.1f}km ahead."
    ),
    "adj_visual_contact": (
        "瞭望员报告目视确认：{name}。方位正前方。",
        "Lookout reports visual confirmation: {name}. Dead ahead."
    ),
    "adj_norm_visual_contact": (
        "「我看到他了！」瞭望员喊了一声：{name}。",
        "'I see 'em!' The lookout calls out: {name}."
    ),
    "adj_miss": (
        "齐射落点偏离。弹着水柱显示方向偏右。",
        "Salvo short. Splashes indicate fall to starboard."
    ),
    "adj_norm_miss": (
        "副官：「没打中……水花偏右了。」",
        "Adjutant: 'Missed... splashes to starboard.'"
    ),
    "adj_enemy_ship_sunk": (
        "观测到{name}发生剧烈殉爆——迅速沉没。",
        "Massive explosion observed on {name} — sinking rapidly."
    ),
    "adj_norm_enemy_ship_sunk": (
        "副官推了推帽子：「{name}炸了。没了。」",
        "The adjutant tips his cap: '{name}'s gone. Just like that.'"
    ),
    "adj_speed_drop": (
        "航速下降。轮机舱报告蒸汽管路受损。",
        "Speed dropping. Engine room reports steam line damage."
    ),
    "adj_norm_speed_drop": (
        "轮机舱传来话：「跑不快了，蒸汽管道破了！」",
        "Engine room: 'Can't make speed — steam line's ruptured!'"
    ),
    "adj_comm_damage": (
        "通讯设备受损。部分天线失效。",
        "Communication gear damaged. Some antennas out."
    ),
    "adj_norm_comm_damage": (
        "副官拍了拍耳机：「通讯器材被震坏了。」",
        "The adjutant taps his headset: 'Comms are busted.'"
    ),
    "adj_radar_damage": (
        "雷达系统可能受损。",
        "Radar system may be damaged."
    ),
    "adj_norm_radar_damage": (
        "雷达兵喊：「长官，雷达不亮了！」",
        "Radar operator: 'Sir, the radar's dead!'"
    ),
    "adj_crippled_ship": (
        "敌舰{name}受重创，航速大幅下降。",
        "Enemy vessel {name} is crippled, speed severely reduced."
    ),
    "adj_norm_crippled_ship": (
        "副官举起望远镜：「{name}不行了，在打转。」",
        "Adjutant with binoculars: '{name}'s done for — she's turning slow.'"
    ),
    "mac_intro": (
        "通讯官抬头：「长官，南达科他号来电——麦克阿瑟上校等待指示。」",
        "Comm officer: 'Sir, South Dakota signals — Captain MacArthur standing by for orders.'"
    ),
    "mac_01": ("通讯官：「南达科他号回复：『收到。保持阵位。』」", "Radio: 'SoDak acknowledges. Maintaining position.'"),
    "mac_02": ("通讯官：「南达科他号回复：『转向完成。跟在后面。』」", "Radio: 'SoDak: Turn completed. Following astern.'"),
    "mac_04": ("通讯官：「南达科他号回复：『好。让他们尝尝。』」", "Radio: 'SoDak: Good. Let them have it.'"),
    "mac_05": ("通讯官：「南达科他号回复：『收到。保持掩护。』」", "Radio: 'SoDak: Received. Covering.'"),
    "mac_random": [
        "无线电传来麦克阿瑟粗哑的声音：「舰长不在后方。我就在这里。」",
        "无线电噼啪作响：「保持进攻！永远保持进攻！」——麦克阿瑟。",
        "麦克阿瑟的声音从无线电里传来：「我回来了。」",
        "南达科他号发来信号：「海军的规矩我懂，舰长。」",
    ],
    "mac_random_en": [
        "MacArthur over radio: 'A captain's place is not in the rear. My place is here.'",
        "Radio crackles: 'Keep attacking! Always attacking!' — MacArthur.",
        "MacArthur's voice on the radio: 'I have returned.'",
        "SoDak signals: 'I know Navy regs, Captain.'",
    ],
    "cmd_help_hard": (
        "\n  命令格式：\n    航向 <0-360>      设定航向\n    航速 <5-33>       指定航速\n    全速              最高航速\n    电令麦克阿瑟 跟进  命令南达科他号跟随\n    电令麦克阿瑟 掩护  命令南达科他号掩护右翼\n    状态              态势报告\n    退出",
        "\n  Commands:\n    heading <0-360>    Set course\n    speed <5-33>       Set speed\n    flank              Flank speed\n    signal MacArthur   Order SoDak\n    status             Situation report\n    quit               Quit"
    ),
    "cmd_help_norm": (
        "\n  你可以：\n    航向 <0-360>      转弯到多少度\n    航速 <5-33>       跑多快\n    全速              油门踩到底\n    电令 跟进     让南达科他跟着你\n    电令 掩护     让南达科他掩护右翼\n    状态              看看现在啥情况\n    退出              不打了",
        "\n  You can:\n    heading <0-360>    Turn to heading\n    speed <5-33>       Set speed\n    flank              Go max speed\n    signal macarthur  Order SoDak\n    status             Check status\n    quit               Quit the game"
    ),
    "no_event": ("    无特殊观察。", "    Nothing to report."),
    "sunk": ("\n  ✖ 依阿华号沉没。战斗结束。", "\n  ✖ Iowa sunk. Battle over."),
    "victory": ("\n  ✓ 敌舰队失去战斗力。美军胜利。", "\n  ✓ Enemy fleet neutralized. US victory."),
    "mode_prompt": (
        "\n  选择游戏模式：\n    1. 硬核模式——军事条例，海军规范，对白严谨\n    2. 普通人模式——自然语言，容易理解\n  输入 1 或 2：",
        "\n  Select mode:\n    1. Hardcore — full military regulation tone\n    2. Normal — natural language, plain speech\n  Enter 1 or 2: "
    ),
}

def make_report(game, player, last_events, turn_num):
    """Fully bilingual adjutant-voiced action report.
    Handles both structured dict events and legacy string events."""
    cn = game.cn
    hard = getattr(game, "_hardcore", True)
    obs = {}  # observations dict: key -> (cn_text, en_text, order)
    order = [0]
    sodak = game.get_ship("south_dakota")

    def add_obs(key, cn_txt, en_txt):
        if key not in obs:
            order[0] += 1
            obs[key] = [cn_txt, en_txt, order[0]]

    def is_dict_ev(e):
        return isinstance(e, dict) and "phase" in e

    # === 1. Normalize events into observations ===
    for e in last_events:
        if is_dict_ev(e):
            # Structured event
            phase = e.get("phase", "")
            etype = e.get("type", "")
            ship = e.get("ship", "")
            target = e.get("target", "")
            desc = e.get("desc", "")
            msg = e.get("msg", "")

            if phase == "radar" and etype == "status":
                if "故障" in msg or "fail" in msg.lower() or "drop" in msg.lower():
                    add_obs("radar_down",
                        "雷达指示：SG雷达回波消失。" if hard else "副官：「雷达没了。」",
                        "Radar: SG signal lost."
                    )
                elif "恢复" in msg or "正常" in msg or "restore" in msg.lower():
                    add_obs("radar_up",
                        "雷达指示：SG雷达恢复，回波清晰。" if hard else "副官：「雷达回来了。」",
                        "Radar: SG restored. Returns stable."
                    )

            elif phase == "sink":
                nm = ship.split()[0] if " " in ship else ship
                add_obs(f"sink_{ship}",
                    f"观测到{nm}发生剧烈殉爆——沉没。" if hard else f"副官推了推帽子：「{nm}炸了。没了。」",
                    f"{nm} observed exploding — sunk."
                )

            elif phase == "torpedo_hit":
                dmg = e.get("dmg", 0)
                nm = target.split()[0] if " " in target else target
                add_obs(f"torp_{target}",
                    f"鱼雷命中{nm}！损害严重。" if hard else f"副官：「鱼雷！打中了！」",
                    f"Torpedo hit on {nm}! Heavy damage."
                )

            elif phase == "fire":
                add_obs("fire",
                    "起火。损管组已就位。" if hard else "副官：「开始冒烟了！损管队在灭火。」",
                    "Fire aboard. Damage control responding."
                )

            elif phase == "flood":
                sev = e.get("severity", "")
                level = e.get("level", 0)
                if level > 20:
                    add_obs("flood",
                        "进水严重！抽水机全开。" if hard else "副官：「水涌进来了！」",
                        "Heavy flooding! Pumps at maximum."
                    )
                elif level > 5:
                    add_obs("flood",
                        "进水。正在排水中。" if hard else "副官：「有点进水。」",
                        "Flooding reported. Pumps running."
                    )

        else:
            # Legacy string event — parse with regex
            estr = str(e)

            if "[火灾]" in estr or "fire" in estr.lower():
                add_obs("fire",
                    "起火。损管组已就位。" if hard else "副官：「开始冒烟了！损管队在灭火。」",
                    "Fire aboard. Damage control responding."
                )

            if "[沉没]" in estr or "[sink]" in estr.lower():
                m = re.search(r"沉没](.*?)沉没", estr) or re.search(r"sink\](.*)", estr, re.I)
                if m:
                    nm = m.group(1).strip()
                else:
                    # Try extracting ship name
                    parts = estr.replace("[沉没]", "").replace("[sink]", "").strip()
                    nm = parts
                add_obs("sink_" + nm,
                    f"观测到{nm}沉没。" if hard else f"副官：「{nm}没了。」",
                    f"{nm} sunk."
                )

            if "[鱼雷]" in estr or "torpedo" in estr.lower():
                add_obs("torpedo",
                    "鱼雷接触。" if hard else "副官：「鱼雷！」",
                    "Torpedo contact!"
                )

            if "雷达" in estr and "故障" in estr:
                add_obs("radar_down",
                    "雷达指示：SG雷达回波消失。" if hard else "副官：「雷达没了。」",
                    "Radar: SG signal lost."
                )
            elif "雷达" in estr and ("恢复" in estr or "正常" in estr):
                add_obs("radar_up",
                    "雷达指示：SG雷达恢复，回波清晰。" if hard else "副官：「雷达回来了。」",
                    "Radar: SG restored. Returns stable."
                )

    # === 2. Fire status from ship state ===
    fires = player.get("fires", [])
    flood = player.get("flood_level", 0)
    lst = player.get("list_deg", 0)
    cur_spd = player.get("speed_kt", 30)
    prev_spd = getattr(player, "_prev_speed", cur_spd)

    if fires:
        add_obs("state_fire",
            f"舰上起火{len(fires)}处。损管组正在灭火。" if hard else f"副官：「着火了{len(fires)}处！」",
            f"Shipboard fire: {len(fires)} locations."
        )
    if flood > 15:
        add_obs("state_flood",
            "进水——舰体下沉。" if hard else "副官：「船在下沉。」",
            "Flooding — ship is settling."
        )
    elif flood > 5:
        add_obs("state_flood",
            "轻微进水。" if hard else "副官：「有点漏水。」",
            "Minor flooding."
        )
    if lst > 5:
        side = "右" if lst > 0 else "左"
        add_obs("state_list",
            f"舰体向{side}侧倾{abs(lst):.0f}度。正在注水调整。" if hard else f"副官：「船向{side}歪了{abs(lst):.0f}度。」",
            f"Listing {abs(lst):.0f} deg to {side}."
        )
    if cur_spd < prev_spd - 3:
        add_obs("state_speed",
            "航速下降。轮机舱报告蒸汽管路受损。" if hard else "轮机舱传来话：「跑不快了！」",
            "Speed dropping. Engine room reports damage."
        )
    player["_prev_speed"] = cur_spd

    # === 3. SoDak status ===
    if sodak and not sodak.get("sunk", False):
        d = game.distance_between(player, sodak)
        hp_pct = sodak.get("hp", 1) / max(sodak.get("max_hp", 1), 1)
        if hp_pct < 0.3:
            add_obs("sodak_state",
                f"南达科他号受重创。距离{d:.1f}公里。" if hard else f"副官看了看船尾：「南达科他号伤得不轻。距离{d:.1f}公里。」",
                f"South Dakota heavily damaged. Range {d:.1f}km."
            )
    elif sodak and sodak.get("sunk", False):
        add_obs("sodak_lost",
            "长官……南达科他号失去联系。" if hard else "副官低声说：「南达科他号……没回应了。」",
            "South Dakota has gone silent."
        )

    # === 4. Gunnery from engine events ===
    gunnery_hits = set()
    gunnery_hit_descs = set()
    for e in last_events:
        if is_dict_ev(e) and e.get("phase") == "gunnery":
            tgt = e.get("target", "")
            if e.get("type") == "hit" and tgt:
                gunnery_hits.add(tgt)
            if e.get("type") == "location" and tgt:
                gunnery_hit_descs.add((tgt, e.get("location", "")))
        elif not is_dict_ev(e) and "[炮击]" in str(e) and "命中" in str(e):
            for js in game.active_ships("JP"):
                jk = js["name"].split()[-1].lower()
                if jk in str(e).lower():
                    gunnery_hits.add(js["name"])
                    for loc in ["水线","上层","甲板","通讯","雷达"]:
                        if loc in str(e) or loc.encode('utf-8') in [str(e).encode('utf-8')]:
                            gunnery_hit_descs.add((js["name"], loc))

    if len(gunnery_hits) >= 2:
        names = [n.split()[0] if " " in n else n for n in gunnery_hits]
        add_obs("gunnery_multi",
            f"命中多发：{', '.join(names)}。" if hard else f"副官：「又中了！{', '.join(names)}！」",
            f"Multiple hits: {', '.join(names)}."
        )
    elif len(gunnery_hits) == 1:
        nm = list(gunnery_hits)[0]
        short = nm.split()[0] if " " in nm else nm
        add_obs("gunnery_hit",
            f"命中{short}。" if hard else f"副官：「打中了{short}！」",
            f"Hit on {short}."
        )

    # Check if we got hit
    us_hit = any(
        (is_dict_ev(e) and e.get("phase") in ("damage","torpedo_hit") and
         ("iowa" in e.get("ship","").lower() or "south_dakota" in e.get("ship","").lower()))
        for e in last_events
    ) or any(
        not is_dict_ev(e) and ("iowa" in str(e).lower() or "south_dakota" in str(e).lower())
        and ("命中" in str(e) or "hit" in str(e).lower())
        for e in last_events
    )

    if us_hit:
        add_obs("taking_fire",
            "中弹！损害管制组就位！" if hard else "船体一震。副官抓住海图桌边缘：「我们中弹了！」",
            "Hit taken! Damage control parties to stations!"
        )

    # === 5. Final adjutant line ===
    if not obs:
        add_obs("nothing",
            "副官保持沉默。海图室里只有钟声。" if not hard else "无特殊观察。",
            "The adjutant is quiet." if not hard else "Nothing to report."
        )

    # === 6. Render ===
    sorted_obs = sorted(obs.values(), key=lambda x: x[2])
    return [f"    {o[0] if cn else o[1]}" for o in sorted_obs]

# ============================================================
# GAME CLASS
# ============================================================

class Game(bt.Battle):
    def __init__(self, seed=None):
        super().__init__("Midway North", seed or 111)
        self.player_ship = None
        self.setup_battle()
        self.player_ship = self.get_ship("iowa")
        self.cn = True
        self._hardcore = True
        self.tc = 0
        self._reported_contacts = set()
        self._prev_speed = self.player_ship["speed_kt"]
        # Pre-battle MC: roll Yukikaze buffs
        self._pre_battle_mc_done = False

    def set_lang(self, text):
        self.cn = has_chinese(text)

    def set_mode(self, hard):
        self._hardcore = hard

    def run_tick(self):
        self.tc += 1
        self.turn += 1
        self.time_minutes += 3
        ev = []
        # First turn: pre-battle MC check
        if self.turn == 1:
            mc_lines = self.pre_battle_mc()
            if mc_lines:
                ev.extend(mc_lines)
        ev.extend(self.radar_phase())
        ev.extend(self.detection_phase())
        for s in self.active_ships():
            self.move_ship(s)
        ev.extend(self.torpedo_launch_phase())
        ev.extend(self.torpedo_phase())
        ev.extend(self.gunnery_phase())
        ev.extend(self.secondary_gunnery_phase())
        ev.extend(self.damage_progression())
        ev.extend(self.sink_check())
        return ev

    def pre_battle_mc(self):
        """Pre-battle Monte Carlo: roll Yukikaze buffs and announce."""
        if self._pre_battle_mc_done:
            return []
        self._pre_battle_mc_done = True
        yuki = self.get_ship("yukikaze")
        if not yuki:
            return []
        active_ids = buffs.roll_buffs()
        yuki["_buffs"] = active_ids
        yuki["_mods"] = buffs.get_modifiers(active_ids)
        if not active_ids:
            return []
        mods = yuki["_mods"]
        if mods.get("evasion_bonus_pct", 0):
            yuki["_evasion_bonus"] = yuki.get("_evasion_bonus", 0) + mods["evasion_bonus_pct"]
        if mods.get("torpedo_dodge_pct", 0):
            yuki["_torpedo_evade"] = yuki.get("_torpedo_evade", 0) + mods["torpedo_dodge_pct"]
        if mods.get("magazine_safe_pct", 0):
            yuki["_magazine_protect"] = mods["magazine_safe_pct"]
        if mods.get("critical_resist_pct", 0):
            yuki["_crit_resist"] = mods["critical_resist_pct"]
        cn = self.cn
        flavor = buffs.describe_buffs(active_ids, cn=cn)
        lines = []
        lines.append("")
        lines.append("    [蒙特卡洛推演]" if cn else "    [Monte Carlo Analysis]")
        lines.append("")
        for ft in flavor:
            lines.append(f"    {ft}")
        lines.append(f"    雪风号获得{len(active_ids)}层幸运祝福。" if cn else f"Yukikaze receives {len(active_ids)} layers of fortune blessing.")
        lines.append("")
        lines.append("    [战场态势确认完毕]" if cn else "    [Battle space confirmed]")
        return lines


    def show_briefing(self):
        iowa_s = self.get_ship("iowa")
        sodak_s = self.get_ship("south_dakota")
        bb_list = sorted([s for s in self.active_ships("JP") if s.get("displacement",0) > 10000], key=lambda x: -x["displacement"])
        dd_list = sorted([s for s in self.active_ships("JP") if s.get("displacement",0) <= 10000], key=lambda x: x["name"])

        # Intro crawl
        print("=" * 66)
        if self.cn:
            print()
            print("  平行时空 · 1942年6月5日 · 北纬30度14分 东经178度36分")
            print()
            print("  萨沃岛海战后，历史发生偏移。联合舰队没有撤退——")
            print("  山本五十六下令乘胜直取中途岛。")
            print()
            print("  美军察觉日军的意图。华盛顿紧急调遣最新锐的战列舰——")
            print("  USS 衣阿华号——前往拦截。与南达科他号组成编队，")
            print("  在黑夜中向西北方高速前进。")
            print()
            print("  你的舰桥上多了一个人——海军上校阿利·伯克，")
            print("  舰长驱逐舰中队出身，夜战和雷达战术的高手。")
            print("  他是你的副官，是舰桥上的第二双眼睛。")
            print()
            print("  南达科他号在两公里外，麦克阿瑟上校在舰桥上等着你的信号。")
        else:
            print()
            print("  Parallel Universe · June 5, 1942 · 30N 178E")
            print()
            print("  After Savo Island, history shifted. The Combined Fleet did not withdraw —")
            print("  Yamamoto ordered a thrust straight for Midway.")
            print()
            print("  Washington scrambles the newest battleship — USS Iowa — to intercept.")
            print("  Paired with South Dakota, your task group steams NW through the night.")
            print()
            print("  There is one extra man on your bridge — Captain Arleigh Burke, USN.")
            print("  Destroyer squadron veteran. Night-fighter. Radar tactician.")
            print("  He is your adjutant. Your second set of eyes.")
            print()
            print("  South Dakota rides 2km off your starboard quarter. Capt. MacArthur waits.")
        print("=" * 66)

        # Force list
        print(f"\n>>> {'作战简报' if self.cn else 'BRIEFING'}\n")
        print(f"  {'时间：1942年6月5日  凌晨2点' if self.cn else 'Time: June 5, 1942  02:00'}")
        print(f"  {'天气：阴天，无月光，能见度15公里' if self.cn else 'Wx: Overcast, no moon, 15km vis'}")
        print(f"  {'雷达在30公里外发现敌舰队' if self.cn else 'Radar detects enemy fleet at 30km'}")

        print(f"\n  {'【你方舰队】' if self.cn else '[YOUR FORCE]'}")
        cnk = cn_name
        if self.cn:
            print(f"    1. {cnk('iowa'):15s} — 战列舰  {iowa_s['displacement']}吨  全长{iowa_s['length_m']:.0f}米  最高{iowa_s['speed_max_kt']}节")
            print(f"       主炮：16英寸炮9门（三联装炮塔×3）  配有对海搜索雷达")
            print(f"    2. {cnk('south_dakota'):15s} — 战列舰  {sodak_s['displacement']}吨  全长{sodak_s['length_m']:.0f}米  最高{sodak_s['speed_max_kt']}节")
            print(f"       主炮：16英寸炮9门（三联装炮塔×3）  配有对海搜索雷达")
        else:
            print(f"    1. USS Iowa           — Battleship  {iowa_s['displacement']}t  {iowa_s['length_m']:.0f}m  {iowa_s['speed_max_kt']}kt")
            print(f"       Main: 16-inch x9 (3x3)  Radar equipped.")
            print(f"    2. USS South Dakota   — Battleship  {sodak_s['displacement']}t  {sodak_s['length_m']:.0f}m  {sodak_s['speed_max_kt']}kt")
            print(f"       Main: 16-inch x9 (3x3)  Radar equipped.")

        print(f"\n  {'【日军舰队】' if self.cn else '[JAPANESE FORCE]'}")
        print(f"   {'── 战列舰 4艘 ──' if self.cn else '── 4 Battleships ──'}")
        for e in bb_list:
            nm = cnk(e.get('_key','')) if self.cn else e['name']
            if self.cn:
                print(f"    {nm:12s}  {e['displacement']}吨  主炮{e['main_guns']}门{e['main_caliber_mm']//10:.0f}厘米炮  最高{e['speed_max_kt']}节")
            else:
                print(f"    {nm:22s}  {e['displacement']}t  {e['main_guns']}x{e['main_caliber_mm']}mm  {e['speed_max_kt']}kt")
        print(f"   {'── 驱逐舰 5艘 ──' if self.cn else '── 5 Destroyers ──'}")
        for e in dd_list:
            nm = cnk(e.get('_key','')) if self.cn else e['name']
            if self.cn:
                print(f"    {nm:12s}  主炮{e['main_guns']}门{e['main_caliber_mm']//10:.1f}厘米炮  最高{e['speed_max_kt']}节  配氧气鱼雷")
            else:
                print(f"    {nm:22s}  {e['main_guns']}x{e['main_caliber_mm']}mm  {e['speed_max_kt']}kt  Type93 torp")

        n = self.get_ship("nagato")
        if n:
            d = self.distance_between(self.player_ship, n)
            nm = cnk("nagato") if self.cn else n['name']
            if self.cn:
                print(f"\n  当前距{nm}：约{d:.0f}公里")
                print("  敌舰队航向：330度  航速：大约18到22节")
                print("  我舰队航向：150度  航速：20节")
                print("\n  [!] 注意：日军配备九三式氧气鱼雷 — 航迹几乎看不见，射程40公里")
                print("      装药接近500公斤。不会自动报警。")
            else:
                print(f"\n  Range to {nm}: ~{d:.0f}km")
                print("  Enemy course: 330  Speed: 18-22kt")
                print("  Our course: 150  Speed: 20kt")
                print("\n  [!] WARNING: Type93 oxygen torpedoes — near-invisible, 40km range")
                print("      ~500kg warhead. No auto-warning.")
        print("=" * 66)


# ============================================================
# COMMAND PARSER
# ============================================================

def cmd_parse(text, game):
    p = game.player_ship
    cn = game.cn
    results = []

    m = re.search(r'(?:heading|航向|course)\s*(\d+)', text, re.I)
    if m:
        h = int(m.group(1)) % 360
        p["heading"] = h
        results.append(f"  舵角设定，航向{int(h)}度。" if cn else f"  Helm to {int(h)}.")

    m = re.search(r'(?:speed|航速|velocity)\s*(\d+)', text, re.I)
    if m:
        s = max(5, min(35, int(m.group(1))))
        p["speed_kt"] = s
        results.append(f"  车钟：{s}节。" if cn else f"  Telegraph: {s}kt.")

    if re.search(r'(?:flank|全速|max|full)', text, re.I):
        p["speed_kt"] = 30
        results.append(f"  全速。" if cn else "  Flank speed.")

    sodak = game.get_ship("south_dakota")
    if sodak and not sodak["sunk"]:
        cmd_lower = text.lower()
        if any(w in cmd_lower for w in ["麦克","macarthur","mac","南达","sodak","south"]):
            follow = any(w in cmd_lower for w in ["跟进","follow","follow","保持","stay"])
            cover  = any(w in cmd_lower for w in ["掩护","cover","右翼","starboard","侧翼"])
            attack = any(w in cmd_lower for w in ["开火","fire","射击","攻击","attack","engage"])
            if cover:
                sodak["heading"] = (p["heading"] - 5) % 360
                sodak["speed_kt"] = p["speed_kt"] - 1
                results.append("  " + t("mac_05", cn))
            elif attack:
                results.append("  " + t("mac_04", cn))
            else:
                sodak["heading"] = p["heading"]
                sodak["speed_kt"] = p["speed_kt"] - 2
                results.append("  " + t("mac_01", cn))

    return results


# ============================================================
# MAIN LOOP
# ============================================================

if __name__ == "__main__":
    game = Game()
    p = game.player_ship
    mac_cn = LANG["mac_random"]
    mac_en = LANG["mac_random_en"]

    # Show briefing
    game.show_briefing()

    # Mode selection
    first = input("\n  " + ("按回车键开始..." if True else ""))
    game.set_lang(first + "中")
    cn = True

    try:
        mode_input = input(t("mode_prompt", cn))
    except EOFError:
        mode_input = "2"
    game._hardcore = (mode_input.strip() == "1")
    mode_name = "硬核" if game._hardcore else "普通"
    mode_name_en = "HARDCORE" if game._hardcore else "NORMAL"
    print(f"\n  {'模式：' + mode_name if cn else 'Mode: ' + mode_name_en}")
    print(f"\n  {'='*66}")

    # Intro
    cnk = cn_name
    cn_short = cnk('iowa') if cn else 'USS Iowa'
    print(f"\n>>> {'舰桥——' + cn_short if cn else 'Bridge — ' + cn_short}\n")
    print("  02:00 | " + (f"海图桌旁。雷达操作员报告：9个接触，北方偏西。" if cn else "Chart table. Radar operator: 9 contacts, NW quadrant."))
    print(t("adj_intro", cn))
    if game._hardcore:
        print("  伯克： " + t("adj_01", cn))
    else:
        print("  伯克： " + t("adj_norm_01", cn))
    print("\n  " + t("mac_intro", cn))
    print(t("cmd_help_hard" if game._hardcore else "cmd_help_norm", cn))

    turn = 0
    summary_log = []
    jp_initial = len(game.active_ships("JP"))

    while True:
        turn += 1

        # === STATUS ===
        print(f"\n{'='*66}")
        if cn:
            print(f"  [{game.time_minutes:02d}:00]  USS Iowa — 舰桥")
            print(f"  航速{int(p['speed_kt'])}节  航向{int(p['heading'])}度")
        else:
            print(f"  [{game.time_minutes:02d}:00]  USS Iowa — Bridge")
            print(f"  Speed {int(p['speed_kt'])}kt  Heading {int(p['heading'])}deg")

        # Radar
        if p.get("radar_online", True):
            if cn:
                print("  SG雷达——回波稳定。")
            else:
                print("  SG Radar — online, returns stable.")
        else:
            rt = p.get("radar_drop_turns", 0)
            if cn:
                print(f"  SG雷达——离线。预计{rt}回合后恢复。")
            else:
                print(f"  SG Radar — offline, ~{rt} turns to repair.")

        # Damage (observable)
        if p.get("fires"):
            if cn:
                print(f"  🔥 上层建筑起火{len(p['fires'])}处。")
            else:
                print(f"  🔥 {len(p['fires'])} fires in superstructure.")
        if p.get("flood_level", 0) > 2:
            sev = "轻微" if p["flood_level"] < 10 else "中度" if p["flood_level"] < 25 else "严重"
            side = "右" if p.get("list_deg",0) > 0 else "左"
            if cn:
                print(f"  💧 进水{sev}。舰体向{side}侧倾{p.get('list_deg',0):.0f}度。")
            else:
                print(f"  💧 Flooding {sev}. List {abs(p.get('list_deg',0)):.0f}deg.")
        elif abs(p.get("list_deg",0)) > 2:
            side = "右" if p["list_deg"] > 0 else "左"
            if cn:
                print(f"  ⚓ 舰体向{side}侧倾{abs(p['list_deg']):.0f}度。")
            else:
                print(f"  ⚓ List {abs(p['list_deg']):.0f}deg.")

        # Radar contacts — WITH auto-detected ship names (US advantage!)
        contacts = game.active_ships("JP")
        radar_on = p.get("radar_online", True)
        visible = []
        for e in contacts:
            d = game.distance_between(p, e)
            if (radar_on and d < 32):
                nm, cls = classify_ship(e, cn)
                visible.append((nm, cls, d))
            elif d < 12:
                nm, cls = classify_ship(e, cn)
                visible.append((nm, cls, d))

        if visible:
            if cn:
                print(f"  {'雷达' if radar_on else '目视'}接触（已识别）：")
                for nm, cls, d in visible:
                    print(f"    {nm:22s}  {cls}  {d:.1f}公里")
            else:
                print(f"  {'Radar' if radar_on else 'Visual'} contacts (identified):")
                for nm, cls, d in visible:
                    print(f"    {nm:22s}  {cls}  {d:.1f}km")
        else:
            if cn:
                print("  视距内无接触。")
            else:
                print("  No contacts.")

        # SoDak
        sodak = game.get_ship("south_dakota")
        if sodak and not sodak.get("sunk", False):
            d = game.distance_between(p, sodak)
            if cn:
                print(f"  南达科他号——麦克阿瑟，距离{d:.1f}公里。")
            else:
                print(f"  South Dakota — MacArthur, {d:.1f}km.")
            if random.random() < 0.12:
                msg = random.choice(mac_cn) if cn else random.choice(mac_en)
                print(f"  {msg}")
        elif sodak and sodak.get("sunk", False):
            if cn:
                print(f"  南达科他号——信号中断。")
            else:
                print(f"  South Dakota — comms lost.")

        # === COMMAND ===
        try:
            cmd = input(f"\n>> {'命令：' if cn else 'Command: '}")
        except EOFError:
            print(f"\n{'退出。' if cn else 'Bye.'}")
            break

        if not cmd.strip():
            continue
        if cmd.strip().lower() in ["q", "quit", "exit", "退出"]:
            break
        if cmd.strip().lower() in ["help", "帮助", "h", "?"]:
            print(t("cmd_help_hard" if game._hardcore else "cmd_help_norm", cn))
            continue
        if cmd.strip().lower() in ["status", "状态"]:
            continue

        game.set_lang(cmd)
        parse_results = cmd_parse(cmd, game)

        if cn:
            print(f"\n  命令：\n    「{cmd}」")
            for r in parse_results:
                print(f"  {r}")
        else:
            print(f"\n  Command:\n    「{cmd}」")
            for r in parse_results:
                print(f"  {r}")

        # === EXECUTE ===
        events = game.run_tick()

        # === ACTION REPORT ===
        report = make_report(game, p, events, turn)
        if cn:
            print(f"\n  {'─'*50}")
            print(f"  【战报】战斗开始后{game.time_minutes}分钟")
        else:
            print(f"\n  {'─'*50}")
            print(f"  [SITREP] T+{game.time_minutes}")
        for line in report:
            print(line)
        print(f"  {'─'*50}")

        summary_log.append({"turn": turn, "time": game.time_minutes})

        # End check
        if p.get("sunk", False):
            print(t("sunk", cn))
            break
        if not game.active_ships("JP"):
            print(t("victory", cn))
            break

    # === SUMMARY ===
    sodak = game.get_ship("south_dakota")
    print(f"\n{'='*66}")
    if cn:
        print("  战 役 总 结")
    else:
        print("  BATTLE SUMMARY")
    print(f"{'='*66}")

    total_t = len(summary_log)
    final_t = summary_log[-1]["time"] if summary_log else 0
    jp_sunk = jp_initial - len(game.active_ships("JP"))
    us_sunk = 1 if p.get("sunk", False) else 0

    if cn:
        print(f"  战斗：{total_t}回合（{final_t}分钟）")
        print(f"  日军沉没：{jp_sunk}/{jp_initial}  美军沉没：{us_sunk}/2")
        print(f"  依阿华号：{'沉没' if p.get('sunk') else '可航行'}")
        if sodak:
            print(f"  南达科他号：{'沉没' if sodak.get('sunk') else '可航行'}")
        survivors = game.active_ships("JP")
        if survivors:
            print(f"\n  日军残余：")
            for e in survivors:
                print(f"    {e['name']}")
    else:
        print(f"  Duration: {total_t} turns ({final_t}min)")
        print(f"  JP lost: {jp_sunk}/{jp_initial}  US lost: {us_sunk}/2")
        print(f"  Iowa: {'SUNK' if p.get('sunk') else 'Afloat'}")
        if sodak:
            print(f"  SoDak: {'SUNK' if sodak.get('sunk') else 'Afloat'}")
        survivors = game.active_ships("JP")
        if survivors:
            print(f"\n  JP survivors:")
            for e in survivors:
                print(f"    {e['name']}")
    print(f"{'='*66}")
