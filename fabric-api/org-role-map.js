// org-role-map.js
module.exports.ROLE_TO_ORG = {
    // ORG 1
    clerk: "org1",
    superintendent: "org1",
    projectofficer: "org1",

    // ORG 2
    vro: "org2",
    surveyor: "org2",
    revenueinspector: "org2",
    mro: "org2",
    revenuedepofficer: "org2",

    // ORG 3
    jointcollector: "org3",
    districtcollector: "org3",
    ministryofwelfare: "org3"
};

// Normalize and return org
module.exports.getOrgFromRole = function(role) {
    if (!role) return "org1";
    role = role.toLowerCase().replace(/\s+/g, "");
    return module.exports.ROLE_TO_ORG[role] || "org1";
};
