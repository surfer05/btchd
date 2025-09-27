import CoreLocation
import SwiftUI

struct ReviewSheet: View {
    var target: CLLocationCoordinate2D
    var onSubmit: (_ categories: [String], _ rating: Int, _ text: String) -> Void
    @Environment(\.dismiss) private var dismiss

    @State private var selectedCategories: [String] = []
    @State private var rating: Int = 0
    @State private var notes: String = ""

    private let availableCategories = [
        "Food", "Service", "Atmosphere", "Price", "Location", 
        "Cleanliness", "Accessibility", "Parking", "WiFi", "Noise"
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
                            Text(selectedCategories.isEmpty ? "Select categories..." : "\(selectedCategories.count) selected")
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
                        onSubmit(selectedCategories, rating, notes.trimmingCharacters(in: .whitespacesAndNewlines))
                        dismiss()
                    }
                    .disabled(selectedCategories.isEmpty || rating == 0)
                }
            }
        }
    }
}
