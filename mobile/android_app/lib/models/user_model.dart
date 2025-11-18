class UserModel {
  final String id;
  final String email;
  final String name;
  final String? picture;
  final String role;
  final String? department;
  final String? yearOfStudy;
  final String? rollNumber;

  UserModel({
    required this.id,
    required this.email,
    required this.name,
    this.picture,
    required this.role,
    this.department,
    this.yearOfStudy,
    this.rollNumber,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'],
      email: json['email'],
      name: json['name'],
      picture: json['picture'],
      role: json['role'],
      department: json['department'],
      yearOfStudy: json['year_of_study'],
      rollNumber: json['roll_number'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'name': name,
      'picture': picture,
      'role': role,
      'department': department,
      'year_of_study': yearOfStudy,
      'roll_number': rollNumber,
    };
  }
}
