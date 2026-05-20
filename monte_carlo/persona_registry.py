#!/usr/bin/env python3
"""
Persona Registry v2 — 九位好汉 + 完整战斗参数系统
每个舰长控制: 移动AI + 命中率 × 伤害 × 装填 × 鱼雷 × 团队协作
"""

PERSONAS = {
    # ==== 1. 宋江·及时雨 — 战略家，旗舰 ====
    "xiucai": {
        "name": "宋江·及时雨",
        "description": "梁山之主，调度全局，均衡型旗舰",
        # 团队组织
        "obedience": 0.90,          # 服从性
        "formation_bond": 0.90,     # 编队凝聚力
        "tactical_coordination": 0.85,  # [新增] 战术配合
        "flag_effect_radius_km": 8.0,   # [新增] 旗舰光环范围
        # 移动/战术
        "aggression": 0.55,
        "adaptability": 0.70,
        "decisiveness": 0.75,
        "range_preference": "medium",
        "retreat_threshold": 0.30,
        "turn_rate_mod": 0.9,
        # 战斗输出
        "accuracy_mod": 1.0,        # 基准命中率
        "damage_mod": 1.0,          # 基准伤害
        "reload_mod": 1.0,          # 基准装填
        "torpedo_accuracy_mod": 1.0,
        "torpedo_trigger_km": 9.0,
        "critical_mod": 1.0,
        "evasion_mod": 1.0,
        "special": "strategist"
    },

    # ==== 2. 高俅·太尉 — 欺下媚上，趁火打劫 ====
    "gaoqiu": {
        "name": "高俅·太尉",
        "description": "看人下菜碟，专挑残血收人头",
        "obedience": 0.50,
        "formation_bond": 0.35,
        "tactical_coordination": 0.30,
        "flag_effect_radius_km": 0,  # 无光环
        "aggression": 0.75,         # 打落水狗时超高
        "adaptability": 0.55,
        "decisiveness": 0.70,
        "range_preference": "medium",
        "retreat_threshold": 0.45,  # 自己惜命
        "turn_rate_mod": 1.0,
        "accuracy_mod": 0.90,       # 武艺平常
        "damage_mod": 1.10,         # 但会补刀
        "reload_mod": 0.90,
        "torpedo_accuracy_mod": 0.85,
        "torpedo_trigger_km": 8.0,
        "critical_mod": 1.10,       # 善于抓机会
        "evasion_mod": 1.10,        # 跑得快
        "special": "opportunist"    # 欺软怕硬: HP<50%的敌人伤害×1.3
    },

    # ==== 3. 西门庆·花太岁 — 外表风光，关键时刻掉链子 ====
    "duanyu": {
        "name": "西门庆·花太岁",
        "description": "张扬炫技，实则贪生怕死",
        "obedience": 0.25,
        "formation_bond": 0.20,
        "tactical_coordination": 0.25,
        "flag_effect_radius_km": 0,
        "aggression": 0.70,         # 看起来猛
        "adaptability": 0.80,
        "decisiveness": 0.50,       # 遇事犹豫
        "range_preference": "long",  # 远程放枪安全
        "retreat_threshold": 0.60,  # 最贪生怕死!
        "turn_rate_mod": 1.2,
        "accuracy_mod": 0.85,       # 炫技但不准
        "damage_mod": 1.05,         # 偶尔狠
        "reload_mod": 1.15,         # 装填快(装样子快)
        "torpedo_accuracy_mod": 0.70, # 鱼雷稀烂
        "torpedo_trigger_km": 12.0,  # 远距发射壮胆
        "critical_mod": 0.80,
        "evasion_mod": 1.20,        # 跑路本领一流
        "special": "coward"         # HP<60%立刻撤退
    },

    # ==== 4. 吴用·智多星 — 阴险诡计多 ====
    "siming": {
        "name": "吴用·智多星",
        "description": "从不正面硬碰，以奇取胜",
        "obedience": 0.65,
        "formation_bond": 0.50,
        "tactical_coordination": 0.80,
        "flag_effect_radius_km": 4.0,  # 辅佐光环
        "aggression": 0.30,          # 最低攻击性（不好战）
        "adaptability": 0.95,        # 最高适应力
        "decisiveness": 0.80,
        "range_preference": "variable",  # 每回合变
        "retreat_threshold": 0.25,
        "turn_rate_mod": 1.0,
        "accuracy_mod": 1.15,         # 算计准
        "damage_mod": 0.85,           # 不出力
        "reload_mod": 0.95,
        "torpedo_accuracy_mod": 1.30,  # 鱼雷算计最准！
        "torpedo_trigger_km": 10.0,
        "critical_mod": 1.25,         # 暗算暴击高
        "evasion_mod": 1.15,
        "special": "trickster"        # 不停变换Target
    },

    # ==== 5. 潘金莲·毒妇 — 外柔内毒，贴脸背刺 ====
    "yukikaze_sim": {
        "name": "潘金莲·毒妇",
        "description": "表面从容靠近，突然致命一击",
        "obedience": 0.35,
        "formation_bond": 0.25,
        "tactical_coordination": 0.30,
        "flag_effect_radius_km": 0,
        "aggression": 0.65,          # 看起来中等
        "adaptability": 0.80,
        "decisiveness": 0.40,        # 犹豫，但下了决心就狠
        "range_preference": "medium",
        "retreat_threshold": 0.30,
        "turn_rate_mod": 1.1,
        "accuracy_mod": 1.05,
        "damage_mod": 1.20,          # 下毒手猛
        "reload_mod": 1.05,
        "torpedo_accuracy_mod": 1.20,
        "torpedo_trigger_km": 6.0,    # 贴脸放雷
        "critical_mod": 1.30,         # 背刺暴击极高!
        "evasion_mod": 0.95,
        "special": "backstab"        # 对高HP目标暴击×1.5
    },

    # ==== 6. 李逵·黑旋风 — 真正的疯狗 ====
    "kagero_sim": {
        "name": "李逵·黑旋风",
        "description": "两把板斧，见船就砍",
        "obedience": 0.05,           # 几乎不服从命令
        "formation_bond": 0.05,      # 无编队概念
        "tactical_coordination": 0.05,
        "flag_effect_radius_km": 0,
        "aggression": 1.0,           # 极限攻击性
        "adaptability": 0.20,        # 只会一种打法
        "decisiveness": 1.0,         # 从不犹豫
        "range_preference": "close",
        "retreat_threshold": 0.0,    # 绝不撤退
        "turn_rate_mod": 1.5,
        "accuracy_mod": 0.80,        # 乱砍不准
        "damage_mod": 0.95,
        "reload_mod": 1.30,          # 装填飞快（乱砍）
        "torpedo_accuracy_mod": 0.60,
        "torpedo_trigger_km": 3.0,   # 贴脸才放
        "critical_mod": 0.70,
        "evasion_mod": 0.80,         # 莽撞，不躲
        "special": "frenzy"          # 距<4km时射速×1.5，命中率-15%
    },

    # ==== 7. 孙二娘·母夜叉 — 披着羊皮的狼 ====
    "isokaze_sim": {
        "name": "孙二娘·母夜叉",
        "description": "十字坡人肉包子铺老板娘，暗算偷袭",
        "obedience": 0.45,
        "formation_bond": 0.30,
        "tactical_coordination": 0.40,
        "flag_effect_radius_km": 0,
        "aggression": 0.60,           # 看起来温和
        "adaptability": 0.75,
        "decisiveness": 0.65,
        "range_preference": "close",   # 诱敌靠近
        "retreat_threshold": 0.25,
        "turn_rate_mod": 1.0,
        "accuracy_mod": 1.10,          # 刀准
        "damage_mod": 1.15,            # 下手狠
        "reload_mod": 0.90,
        "torpedo_accuracy_mod": 1.15,
        "torpedo_trigger_km": 5.5,
        "critical_mod": 1.20,
        "evasion_mod": 1.05,
        "special": "ambusher"         # 从背后接近时精度×1.3
    },

    # ==== 8. 时迁·鼓上蚤 — 搅屎棍 ====
    "shiranui_sim": {
        "name": "时迁·鼓上蚤",
        "description": "偷鸡摸狗，以骚扰代替正面交锋",
        "obedience": 0.30,
        "formation_bond": 0.15,
        "tactical_coordination": 0.50,
        "flag_effect_radius_km": 0,
        "aggression": 0.40,
        "adaptability": 0.85,
        "decisiveness": 0.60,
        "range_preference": "long",     # 远处放冷枪
        "retreat_threshold": 0.35,
        "turn_rate_mod": 1.4,           # 最灵活
        "accuracy_mod": 0.85,
        "damage_mod": 0.70,             # 伤害低
        "reload_mod": 1.20,             # 快
        "torpedo_accuracy_mod": 0.75,
        "torpedo_trigger_km": 13.0,
        "critical_mod": 1.10,
        "evasion_mod": 1.30,            # 最会躲
        "special": "harasser"           # 频繁变向，专挑最近目标打
    },

    # ==== 9. 王英·矮脚虎 — 憋屈到爆发 ====
    "kuroshio_sim": {
        "name": "王英·矮脚虎",
        "description": "平时憋屈，近身时突然暴起",
        "obedience": 0.60,              # 服从命令
        "formation_bond": 0.60,
        "tactical_coordination": 0.40,
        "flag_effect_radius_km": 0,
        "aggression": 0.70,             # 憋着火
        "adaptability": 0.30,           # 固执
        "decisiveness": 0.35,           # 长期犹豫
        "range_preference": "medium",
        "retreat_threshold": 0.35,
        "turn_rate_mod": 0.8,           # 转向慢
        "accuracy_mod": 0.90,
        "damage_mod": 0.90,
        "reload_mod": 0.85,
        "torpedo_accuracy_mod": 1.40,   # 唯一擅长: 鱼雷!
        "torpedo_trigger_km": 5.0,      # 近距
        "critical_mod": 0.90,
        "evasion_mod": 0.85,
        "special": "repressed_burst"    # 距<4km时鱼雷精度×1.5 + 伤害×1.3
    }
}


def get_persona(persona_id):
    return PERSONAS.get(persona_id)


def get_default_persona():
    """Default fallback — standard IJN officer"""
    return {
        "name": "IJN Standard",
        "aggression": 0.65,
        "adaptability": 0.60,
        "decisiveness": 0.65,
        "obedience": 0.80,
        "range_preference": "medium",
        "retreat_threshold": 0.20,
        "torpedo_trigger_km": 8.0,
        "turn_rate_mod": 1.0,
        "formation_bond": 0.70,
        "tactical_coordination": 0.60,
        "flag_effect_radius_km": 0,
        "accuracy_mod": 1.0,
        "damage_mod": 1.0,
        "reload_mod": 1.0,
        "torpedo_accuracy_mod": 1.0,
        "critical_mod": 1.0,
        "evasion_mod": 1.0,
    }


if __name__ == "__main__":
    print("=== 水浒精选·九宫格 v2 (完整战斗参数) ===\n")
    for pid, p in PERSONAS.items():
        print(f"{p['name']:15s} | agg={p['aggression']:.2f} obe={p['obedience']:.2f} "
              f"acc={p['accuracy_mod']:.2f} dmg={p['damage_mod']:.2f} "
              f"torp={p['torpedo_accuracy_mod']:.2f} crit={p['critical_mod']:.2f} "
              f"ev=({p['evasion_mod']:.2f}) {p['special']}")
