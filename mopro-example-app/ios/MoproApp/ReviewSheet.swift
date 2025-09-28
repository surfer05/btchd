import CoreLocation
import SwiftUI

struct ReviewSheet: View {
    var target: CLLocationCoordinate2D
    var proof: Data?
    var publicInputs: Data?
    var onSubmit:
        (_ categories: [String], _ rating: Int, _ text: String, _ submitToChain: Bool) -> Void
    @Environment(\.dismiss) private var dismiss

    @State private var selectedCategories: [String] = []
    @State private var rating: Int = 0
    @State private var notes: String = ""
    @State private var submitToChain: Bool = true

    private let availableCategories = [
        "Office", "Service", "Rich", "Hip", "Tourist",
        "Cleanliness", "Normie", "Parking", "WiFi", "Uni",
    ]

    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                // Notes field at the top
                VStack(alignment: .leading, spacing: 8) {
                    Text("Notes")
                        .font(.headline)
                    TextField("Add your notes here...", text: $notes, axis: .vertical)
                        .textFieldStyle(.roundedBorder)
                        .lineLimit(3...6)
                }

                // Categories dropdown
                VStack(alignment: .leading, spacing: 8) {
                    Text("Categories")
                        .font(.headline)

                    Menu {
                        ForEach(availableCategories, id: \.self) { category in
                            Button(action: {
                                if selectedCategories.contains(category) {
                                    selectedCategories.removeAll { $0 == category }
                                } else {
                                    selectedCategories.append(category)
                                }
                            }) {
                                HStack {
                                    Text(category)
                                    if selectedCategories.contains(category) {
                                        Image(systemName: "checkmark")
                                    }
                                }
                            }
                        }
                    } label: {
                        HStack {
                            Text(
                                selectedCategories.isEmpty
                                    ? "Select categories..."
                                    : "\(selectedCategories.count) selected"
                            )
                            .foregroundColor(selectedCategories.isEmpty ? .secondary : .primary)
                            Spacer()
                            Image(systemName: "chevron.down")
                                .foregroundColor(.secondary)
                        }
                        .padding()
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(8)
                    }

                    // Show selected categories as chips
                    if !selectedCategories.isEmpty {
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 8) {
                                ForEach(selectedCategories, id: \.self) { category in
                                    HStack(spacing: 4) {
                                        Text(category)
                                            .font(.caption)
                                        Button(action: {
                                            selectedCategories.removeAll { $0 == category }
                                        }) {
                                            Image(systemName: "xmark.circle.fill")
                                                .font(.caption)
                                                .foregroundColor(.secondary)
                                        }
                                    }
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 4)
                                    .background(Color.blue.opacity(0.1))
                                    .foregroundColor(.blue)
                                    .cornerRadius(12)
                                }
                            }
                            .padding(.horizontal, 1)
                        }
                    }
                }

                // Star rating UI
                VStack(alignment: .leading, spacing: 8) {
                    Text("Rating")
                        .font(.headline)

                    HStack(spacing: 4) {
                        ForEach(1...5, id: \.self) { star in
                            Button(action: {
                                rating = star
                            }) {
                                Image(systemName: star <= rating ? "star.fill" : "star")
                                    .font(.title2)
                                    .foregroundColor(star <= rating ? .yellow : .gray)
                            }
                        }
                    }
                }

                // Onchain submission toggle
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Toggle("Submit to Blockchain", isOn: $submitToChain)
                            .font(.headline)
                        Spacer()
                    }

                    if submitToChain {
                        VStack(alignment: .leading, spacing: 4) {
                            HStack {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundColor(.green)
                                Text("Proof will be verified onchain")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }

                            if proof != nil {
                                HStack {
                                    Image(systemName: "checkmark.circle.fill")
                                        .foregroundColor(.green)
                                    Text("Zero-knowledge proof ready")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                }
                            } else {
                                HStack {
                                    Image(systemName: "exclamationmark.triangle.fill")
                                        .foregroundColor(.orange)
                                    Text("No proof available")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                }
                            }
                        }
                        .padding(.leading, 8)
                    }
                }

                Spacer()
            }
            .padding()
            .navigationTitle("Add Review")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Submit") {
                        onSubmit(
                            selectedCategories, rating,
                            notes.trimmingCharacters(in: .whitespacesAndNewlines), submitToChain)
                        dismiss()
                    }
                    .disabled(selectedCategories.isEmpty || rating == 0)
                }
            }
        }
    }
}
